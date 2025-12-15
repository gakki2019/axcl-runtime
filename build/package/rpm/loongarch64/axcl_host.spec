Name:     axcl_host
Version:  %{?SDK_VERSION:%{SDK_VERSION}}%{!?SDK_VERSION:1.0}
Release:  %{?SDK_RELEASE:%{SDK_RELEASE}}%{!?SDK_RELEASE:1}%{?dist}
Summary:  The "axcl_host" package is used for multimedia data exchange between the host and AX PCIe devices.
Provides: libspdlog.so.1.14()(64bit)
Vendor:   AXERA
URL:      https://www.axera-tech.com/
Group:    System/Kernel

%define _lib /lib
%define _libdir %{_exec_prefix}%{_lib}
%define __strip /bin/true
%define module_version  1.0
%define module_name axcl

%global __requires_exclude ^libaxclrt_worker.*$

License:  GPL
Packager: xiaoqiang <xiaoqiang@axera-tech.com>
Source0:  %{_topdir}/SOURCE/axcl.tar.gz

Requires(post): gcc >= 14.1.0, make, patch, kernel-devel, kernel-headers
Requires:       gcc, kmod, udev
Recommends:     dkms

%description
This package contains PCIe driver, samples, binaries, and libraries.

%prep
%setup -n axcl -q

%install
mkdir -p %{buildroot}%{_bindir}/axcl
mkdir -p %{buildroot}%{_libdir}/axcl
mkdir -p %{buildroot}%{_usrsrc}/%{module_name}-%{module_version}
mkdir -p %{buildroot}%{_includedir}/axcl
mkdir -p %{buildroot}%{_sysconfdir}/ld.so.conf.d
mkdir -p %{buildroot}%{_sysconfdir}/modules-load.d
mkdir -p %{buildroot}%{_sysconfdir}/udev/rules.d
mkdir -p %{buildroot}%{_sysconfdir}/profile.d
mkdir -p %{buildroot}%{_lib}/firmware/axcl
mkdir -p %{buildroot}%{_lib}/modules/$(uname -r)/extra
cp -rf %{_builddir}/axcl/image/ax650_card.pac %{buildroot}%{_lib}/firmware/axcl
cp -rf %{_builddir}/axcl/axcl.conf %{buildroot}%{_sysconfdir}/ld.so.conf.d
cp -rf %{_builddir}/axcl/axcl_pcie.conf %{buildroot}%{_sysconfdir}/modules-load.d
cp -rf %{_builddir}/axcl/axcl_host.rules %{buildroot}%{_sysconfdir}/udev/rules.d
cp -rf %{_builddir}/axcl/axcl.sh %{buildroot}%{_sysconfdir}/profile.d
cp -rf %{_builddir}/axcl/lib/* %{buildroot}%{_libdir}/axcl
cp -rf %{_builddir}/axcl/bin/* %{buildroot}%{_bindir}/axcl
cp -rf %{_builddir}/axcl/json/* %{buildroot}%{_bindir}/axcl
cp -rf %{_builddir}/axcl/data %{buildroot}%{_bindir}/axcl
cp -rf %{_builddir}/axcl/include/* %{buildroot}%{_includedir}/axcl
cp -rf %{_builddir}/axcl/build %{buildroot}%{_usrsrc}/%{module_name}-%{module_version}
cp -rf %{_builddir}/axcl/drv %{buildroot}%{_usrsrc}/%{module_name}-%{module_version}
cp -rf %{_builddir}/axcl/dkms.conf %{buildroot}%{_usrsrc}/%{module_name}-%{module_version}

%post
cd %{_usrsrc}/%{module_name}-%{module_version}/drv/pcie/driver
os_version=$(cat /etc/os-release | grep '^VERSION_ID=' | cut -d '=' -f2 | tr -d '"')
os_name=$(cat /etc/os-release | grep '^NAME=' | cut -d '=' -f2 | tr -d '"')
if [[ ${os_name} == "CentOS Stream" && ${os_version} == "9" ]]; then
    echo "patch pcie_proc.patch ..."
    patch -p3 < pcie_proc.patch >/dev/null 2>&1
fi

if command -v dkms >/dev/null 2>&1; then
    if dkms status | grep -q "^%{module_name}-%{module_version}"; then
        echo "found in DKMS, removing first ..."
        dkms remove -m %{module_name} -v %{module_version} --all
    fi

    echo "build modules with DKMS ..."
    dkms add -m %{module_name} -v %{module_version}
    if [ $? -eq 0 ]; then
        dkms build -m %{module_name} -v %{module_version}
        if [ $? -eq 0 ]; then
            dkms install -m %{module_name} -v %{module_version}
            if [ $? -ne 0 ]; then
                echo "DKMS install failed, build directly ..."
                DIRECT_COMPILE=1
            fi
        else
            echo "DKMS build failed, build directly ..."
            DIRECT_COMPILE=1
        fi
    else
        echo "DKMS add failed, build directly ..."
        DIRECT_COMPILE=1
    fi
else
    echo "DKMS not found, build directly ..."
    DIRECT_COMPILE=1
fi

if [ "${DIRECT_COMPILE}" = "1" ]; then
    make host=loongarch64 clean all install -j8 >/dev/null 2>&1
    mkdir -p %{_lib}/modules/$(uname -r)/extra
    cp -rf %{_usrsrc}/%{module_name}-%{module_version}/out/axcl_linux_loongarch64/ko/* %{_lib}/modules/$(uname -r)/extra/
fi

depmod -a
ldconfig

modprobe ax_pcie_host_dev
modprobe ax_pcie_msg
modprobe ax_pcie_mmb
modprobe axcl_host
modprobe ax_pcie_p2p_rc

%files
%{_bindir}/axcl
%{_libdir}/axcl
%{_usrsrc}/%{module_name}-%{module_version}
%{_includedir}/axcl
%{_sysconfdir}/ld.so.conf.d/axcl.conf
%{_sysconfdir}/modules-load.d/axcl_pcie.conf
%{_sysconfdir}/udev/rules.d/axcl_host.rules
%{_sysconfdir}/profile.d/axcl.sh
%{_lib}/firmware/axcl

%preun
modprobe -r ax_pcie_p2p_rc
modprobe -r axcl_host
modprobe -r ax_pcie_mmb
modprobe -r ax_pcie_msg
modprobe -r ax_pcie_host_dev

if command -v dkms >/dev/null 2>&1; then
    dkms remove -m %{module_name} -v %{module_version} --all || true
fi

rm -rf %{_lib}/modules/$(uname -r)/extra/ax_*
rm -rf %{_lib}/modules/$(uname -r)/extra/axcl_*
rm -rf %{_usrsrc}/%{module_name}-%{module_version}/build/out
rm -rf %{_usrsrc}/%{module_name}-%{module_version}/out

%postun
depmod -a
ldconfig

%changelog
* Wed Oct 30 2024 xiaoqiang <xiaoqiang@axera-tech.com> - 1.0-1
- Update to 1.0-1
- Add DKMS support