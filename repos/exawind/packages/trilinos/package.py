from spack import *
from spack.pkg.builtin.trilinos import Trilinos as bTrilinos
import os

class Trilinos(bTrilinos):
    variant('stk_unit_tests', default=False,
            description='turn on STK unit tests')
    variant('stk_simd', default=False,
            description='Enable SIMD in STK')

    patch('kokkos.patch', when='+cuda')

    def setup_build_environment(self, env):
        spec = self.spec
        if '+cuda' in spec and '+wrapper' in spec:
            if spec.variants['build_type'].value == 'RelWithDebInfo' or spec.variants['build_type'].value == 'Debug':
                env.append_flags('CXXFLAGS', '-Xcompiler -rdynamic -lineinfo')
            if '+mpi' in spec:
                env.set('OMPI_CXX', spec["kokkos-nvcc-wrapper"].kokkos_cxx)
                env.set('MPICH_CXX', spec["kokkos-nvcc-wrapper"].kokkos_cxx)
                env.set('MPICXX_CXX', spec["kokkos-nvcc-wrapper"].kokkos_cxx)
            else:
                env.set('CXX', spec["kokkos-nvcc-wrapper"].kokkos_cxx)

        if '+rocm' in spec:
            if '+mpi' in spec:
                env.set('OMPI_CXX', self.spec['hip'].hipcc)
                env.set('MPICH_CXX', self.spec['hip'].hipcc)
                env.set('MPICXX_CXX', self.spec['hip'].hipcc)
            else:
                env.set('CXX', self.spec['hip'].hipcc)
            if '+stk' in spec:
                # Using CXXFLAGS for hipcc which doesn't use flags in the spack wrappers
                env.append_flags('CXXFLAGS', '-DSTK_NO_BOOST_STACKTRACE')
                if '~stk_simd' in spec:
                    env.append_flags('CXXFLAGS', '-DUSE_STK_SIMD_NONE')

    def setup_dependent_package(self, module, dependent_spec):
        if '+wrapper' in self.spec:
            # Hardcode nvcc_wrapper path to avoid kokkos-nvcc-wrapper error with trilinos as an external
            self.spec.kokkos_cxx = os.path.join(os.getenv('SPACK_MANAGER'), 'bin', 'nvcc_wrapper')
        else:
            self.spec.kokkos_cxx = spack_cxx

    def cmake_args(self):
        spec = self.spec
        define = CMakePackage.define
        options = super(Trilinos, self).cmake_args()

        if '+stk' in spec:
            options.append(self.define_from_variant('STK_ENABLE_TESTS', 'stk_unit_tests'))

        if '+rocm' in self.spec:
            # Used as an optimization to only list the single specified
            # arch in the offload-arch compile line, but not explicitly necessary
            targets = self.spec.variants['amdgpu_target'].value
            options.append('-DCMAKE_HIP_ARCHITECTURES=' + ';'.join(str(x) for x in targets))
            options.append('-DAMDGPU_TARGETS=' + ';'.join(str(x) for x in targets))
            options.append('-DGPU_TARGETS=' + ';'.join(str(x) for x in targets))

        return options
