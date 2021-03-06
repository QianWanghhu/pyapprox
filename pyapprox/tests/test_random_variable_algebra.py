#!/usr/bin/env python
import unittest
from pyapprox.random_variable_algebra import *
from functools import partial
from scipy import stats
from pyapprox.univariate_quadrature import gauss_hermite_pts_wts_1D,\
    gauss_jacobi_pts_wts_1D


class TestRandomVariableAlgebra(unittest.TestCase):
    def test_scalar_multiple_of_random_variable(self):
        lb, ub = 0, 1
        coef = 2
        xvariable = stats.uniform(lb, ub)
        yvariable = stats.uniform(lb, ub*coef)
        yy = np.linspace(lb, ub*coef, 101)
        ypdf_vals = scalar_multiple_of_random_variable(xvariable.pdf, coef, yy)
        assert np.allclose(yvariable.pdf(yy), ypdf_vals)

    def test_power_of_random_variable_standard_normal_squared(self):
        mean, var = [0, 1]
        power = 2
        variable = stats.norm(mean, np.sqrt(var))
        yy = np.linspace(1e-3, stats.chi2.ppf(0.999, df=1), 101)
        assert np.allclose(
            power_of_random_variable_pdf(variable.pdf, power, yy),
            stats.chi2.pdf(yy, df=1))

    def test_get_inverse_derivatives_cubic_polynomial(self):
        lb, ub = 0, 1
        def function(xx): return (1-xx)**3
        coef = [1, -3, 3, -1]
        poly = np.poly1d(coef[::-1])
        zz = np.linspace(0, 1, 100)
        inverse_vals, inverse_derivs, defined_indices = get_inverse_derivatives(
            poly, [lb, ub], zz)
        assert np.allclose(inverse_vals, 1-zz**(1/3))
        # ignore derivative at 0 which is infinity
        assert np.allclose(inverse_derivs[1:], -1/3*zz[1:]**(-2/3))

    def test_variable_transformation_uniform_cubic_polynomial(self):
        lb, ub = 0, 1
        def function(xx): return (1-xx)**3
        def x_pdf(xx): return (3*(1-xx)**2).squeeze()
        #xx = np.linspace(lb,ub,101);plt.plot(xx,x_pdf(xx));plt.show()
        #xx = np.linspace(lb,ub,101);plt.plot(xx,function(xx));plt.show()
        coef = [1, -3, 3, -1]
        poly = np.poly1d(coef[::-1])
        poly_min, poly_max = get_global_maxima_and_minima_of_monomial_expansion(
            poly, lb, ub)
        # zz_bounds = [poly_min,poly_max]
        # due to singularities at 0 and 1 zz is only defined on 0<zz<1
        # so do not evaluate close to these bounds
        eps = 1e-3
        zz_bounds = [eps, 1-eps]
        zz = np.linspace(zz_bounds[0], zz_bounds[1], 10)
        z_pdf_vals = get_pdf_from_monomial_expansion(coef, lb, ub, x_pdf, zz)
        print(z_pdf_vals)
        assert np.allclose(z_pdf_vals, np.ones(zz.shape[0]), atol=1e-8)

        def x_cdf(tt): return (tt*(tt**2-3*tt+3)).squeeze()
        z_cdf_vals = get_cdf_from_monomial_expansion(coef, lb, ub, x_cdf, zz)
        # plt.plot(zz,z_cdf_vals,label='Approx.')
        # plt.plot(zz,stats.uniform(0,1).cdf(zz),label='True');
        # plt.legend();plt.show()
        assert np.allclose(z_cdf_vals, stats.uniform(0, 1).cdf(zz), atol=1e-8)

    def test_variable_transformation_uniform_cosine_taylor_series_expansion(self):
        lb, ub = np.pi/4, np.pi*2.25
        N = 10
        # approximate x*cos(x)
        from scipy.special import factorial
        def function(
            xx): return xx*(1+np.sum([(-1)**n * (xx)**(2*n)/factorial(2*n) for n in range(1, N+1)], axis=0))
        nonzero_coef = [1]+[(-1)**n * (1)**(2*n)/factorial(2*n)
                            for n in range(1, N+1)]
        coef = np.zeros(2*N+2)
        coef[1::2] = nonzero_coef
        poly = np.poly1d(coef[::-1])
        x_pdf = stats.uniform(lb, ub-lb).pdf
        #xx = np.linspace(lb,ub,101);plt.plot(xx,x_pdf(xx));plt.show()
        #xx = np.linspace(lb,ub,101);plt.plot(xx,function(xx));
        # plt.plot(xx,xx*np.cos(xx));plt.plot(xx,poly(xx),'--');plt.show()
        # poly_min,poly_max = \
        #     get_global_maxima_and_minima_of_monomial_expansion(
        #    poly,lb,ub)
        # zz_bounds = [poly_min,poly_max]
        # due to singularities at 0 and 1 zz is only defined on 0<zz<1
        # so do not evaluate close to these bounds
        zz_bounds = [function(3.42561846)+1e-3, function(6.439062046)-1e-3]
        zz = np.linspace(zz_bounds[0], zz_bounds[1], 101)
        z_pdf_vals = get_pdf_from_monomial_expansion(coef, lb, ub, x_pdf, zz)
        from matplotlib import pyplot as plt
        plt.hist(
            function(np.random.uniform(lb,ub,10001)),density=True,bins=100)
        plt.plot(zz,z_pdf_vals); plt.show()

        x_cdf = stats.uniform(lb, ub-lb).cdf
        z_cdf_vals = get_cdf_from_monomial_expansion(coef, lb, ub, x_cdf, zz)
        fd_eps = 1e-8
        z_cdf_vals_perturbed = get_cdf_from_monomial_expansion(
            coef, lb, ub, x_cdf, zz+fd_eps)
        # fig,axs=plt.subplots(1,2,figsize=(2*8,6))
        critical_points = get_all_local_extrema_of_monomial_expansion_1d(
            poly, lb, ub)
        # xx = np.linspace(lb,ub,101);axs[0].plot(xx,function(xx));
        # axs[0].plot(critical_points,poly(critical_points),'o')
        #zz_rand = np.sort(function(np.random.uniform(lb,ub,10001)))
        #ecdf = np.cumsum(np.ones(zz_rand.shape[0])/zz_rand.shape[0])
        # axs[1].plot(zz_rand,ecdf,label='ECDF')
        # axs[1].plot(zz,z_cdf_vals,label='Approx CDF')
        # axs[1].legend();plt.show()
        #plt.plot(zz,(z_cdf_vals_perturbed-z_cdf_vals)/fd_eps,
        #    label='PDF approx')
        #plt.plot(zz,z_pdf_vals,label='PDF Exact');plt.legend();plt.show()
        # print(np.linalg.norm(
        #    (z_pdf_vals-(z_cdf_vals_perturbed-z_cdf_vals)/fd_eps)))
        assert np.allclose(
            z_pdf_vals, (z_cdf_vals_perturbed-z_cdf_vals)/fd_eps, atol=1e-5)

    def test_variable_transformation_uniform_postive_poly(self):
        coef = [3.22667072e-02, 0.0,  8.10965258e-02,  0.0,
                -2.59111042e-01, 0.0, 1.85351770e-01]
        poly = np.poly1d(coef[::-1])
        function = poly

        lb, ub = -1, 1
        critical_points = get_all_local_extrema_of_monomial_expansion_1d(
            poly, lb, ub)

        x_cdf = stats.uniform(lb, ub-lb).cdf
        zz = np.linspace(min(poly([lb, ub]).min(), poly(critical_points).min(
        ))*1.001, max(poly([lb, ub]).max(),
                      poly(critical_points).max())*0.999, 101)
        z_cdf_vals = get_cdf_from_monomial_expansion(coef, lb, ub, x_cdf, zz)
        zz_rand = np.sort(function(np.random.uniform(lb, ub, 1001)))
        ecdf = np.cumsum(np.ones(zz_rand.shape[0])/zz_rand.shape[0])
        # fig,axs=plt.subplots(1,2,figsize=(2*8,6))
        critical_points = get_all_local_extrema_of_monomial_expansion_1d(
            poly, lb, ub)
        # xx = np.linspace(lb,ub,101);axs[0].plot(xx,function(xx));
        # axs[0].plot(critical_points,poly(critical_points),'o')

        # axs[1].plot(zz_rand,ecdf,label='ECDF')
        #axs[1].plot(zz,z_cdf_vals,label='Approx CDF')
        # plt.legend();plt.show()

    def test_get_inverse_derivatives_x_squared(self):
        lb, ub = -np.inf, np.inf
        mean, var = [0, 1]
        def function(xx): return xx**2
        coef = [0, 0, 1]
        poly = np.poly1d(coef[::-1])
        zz = np.linspace(0, 1, 30)
        inverse_vals, inverse_derivs, defined_indices = get_inverse_derivatives(
            poly, [lb, ub], zz)
        assert np.allclose(inverse_vals, zz**(1/2))
        # ignore derivative at 0 which is infinity
        assert np.allclose(inverse_derivs[1:], 1/2*zz[1:]**(-1/2))

    def test_variable_transformation_standard_normal_squared(test):
        lb, ub = -np.inf, np.inf
        mean, var = [0, 1]
        def function(xx): return xx**2
        x_pdf = stats.norm(mean, np.sqrt(var)).pdf

        coef = [0, 0, 1]
        poly = np.poly1d(coef[::-1])
        # due to singularities at 0 and 1 zz is only defined on 0<zz<1
        # so do not evaluate close to these bounds
        zz_bounds = stats.chi2.interval(0.9, df=1)
        zz = np.linspace(zz_bounds[0], zz_bounds[1], 100)
        z_pdf_vals = get_pdf_from_monomial_expansion(coef, lb, ub, x_pdf, zz)
        # plt.plot(zz,z_pdf_vals,label='Approx.')
        # plt.plot(zz,stats.chi2.pdf(zz,df=1),label='True');
        # plt.legend();plt.show()
        assert np.allclose(z_pdf_vals, stats.chi2.pdf(zz, df=1), atol=1e-8)

        zz_bounds = stats.chi2.interval(0.999, df=1)
        zz = np.linspace(zz_bounds[0], zz_bounds[1], 100)

        x_cdf = stats.norm(mean, np.sqrt(var)).cdf
        z_cdf_vals = get_cdf_from_monomial_expansion(coef, lb, ub, x_cdf, zz)
        # plt.plot(zz,z_cdf_vals,label='Approx.')
        # plt.plot(zz,stats.chi2.cdf(zz,df=1),label='True');
        # plt.legend();plt.show()
        assert np.allclose(z_cdf_vals, stats.chi2.cdf(zz, df=1), atol=1e-8)

    def test_sum_of_independent_uniform_and_gaussian_variables(self):
        lb, ub = 1, 3
        mu, sigma = 0., 0.25
        uniform_dist = stats.uniform(loc=lb, scale=ub-lb)
        normal_dist = stats.norm(loc=mu, scale=sigma)

        pdf1 = uniform_dist.pdf
        pdf2 = normal_dist.pdf

        zz = np.linspace(-3, 3, 100)
        # using gauss hermite quadrature does not work because it is
        # using polynomial quadrature to integrate a discontinous function
        # i.e. uniform PDF
        #x,w = gauss_hermite_pts_wts_1D(100)
        # x = x*sigma+mu #scale from standard normal
        # conv_pdf = sum_of_independent_random_variables_pdf(
        #    pdf1,[[x,w]],zz)

        # but since normal PDF is smooth integration in reverse order works well
        x, w = gauss_jacobi_pts_wts_1D(100, 0, 0)
        x = x+2  # scale from [-1,1] to [1,3]
        conv_pdf = sum_of_independent_random_variables_pdf(
            pdf2, [[x, w]], zz)

        #plt.plot(zz, pdf1(zz), label='Uniform')
        #plt.plot(zz, pdf2(zz), label='Gaussian')
        #plt.plot(zz,conv_pdf, label='Sum')
        #plt.legend(loc='best'), plt.suptitle('PDFs')
        # plt.show()

    def test_sum_of_independent_gaussian_variables(self):
        nvars = 3
        means = np.random.uniform(-1, 1, nvars)
        variances = np.random.uniform(0.5, 1.5, nvars)

        pdfs = [stats.norm(loc=means[ii], scale=np.sqrt(variances[ii])).pdf
                for ii in range(nvars)]

        zz = np.linspace(-3, 3, 60)
        from pyapprox.univariate_quadrature import gauss_hermite_pts_wts_1D
        x, w = gauss_hermite_pts_wts_1D(100)
        quad_rules = [[x*np.sqrt(variances[ii])+means[ii], w]
                      for ii in range(1, nvars)]
        conv_pdf = sum_of_independent_random_variables_pdf(
            pdfs[0], quad_rules, zz)

        true_pdf = stats.norm(
            loc=means.sum(), scale=np.sqrt(variances.sum())).pdf
        assert np.allclose(true_pdf(zz), conv_pdf)

    def test_product_of_independent_gaussian_variables(self):
        nvars = 2
        means = np.zeros(nvars)
        variances = np.ones(nvars)

        pdfs = [stats.norm(loc=means[ii], scale=np.sqrt(variances[ii])).pdf
                for ii in range(nvars)]

        # the product transformation is not defined at zero.
        # gauss quadrature rule accuracy is poor because of this. Perhaps
        # use mixture of two truncated normal distributions one on each side
        # of zero.
        eps = 0.2
        zz = np.linspace(-3, -eps, 100)
        zz = np.concatenate((zz, -zz[::-1]))
        from pyapprox.univariate_quadrature import gauss_hermite_pts_wts_1D
        x, w = gauss_hermite_pts_wts_1D(200)
        quad_rules = [[x*np.sqrt(variances[ii])+means[ii], w]
                      for ii in range(1, nvars)]
        product_pdf = product_of_independent_random_variables_pdf(
            pdfs[0], quad_rules, zz)

        from scipy.special import kn as modified_bessel_2nd_kind

        def exact_product_two_zero_mean_independent_gaussians(var1, var2, zz):
            tmp = np.sqrt(var1*var2)
            vals = modified_bessel_2nd_kind(0, np.absolute(zz)/tmp)/(np.pi*tmp)
            return vals

        true_pdf = exact_product_two_zero_mean_independent_gaussians(
            variances[0], variances[1], zz)
        # for ii in range(nvars):
        #     plt.plot(zz, pdfs[ii](zz),label=r'$X_%d$'%ii)
        # plt.plot(zz,true_pdf, label='Product')
        # plt.plot(zz,product_pdf, '--', label='True Product')
        # plt.legend()
        # plt.show()
        assert np.linalg.norm(true_pdf-product_pdf, ord=np.inf) < 0.03

    def test_product_of_independent_uniform_variables(self):
        nvars = 3
        pdfs = [stats.uniform(0, 1).pdf]*nvars

        # transfomation not defined at 0
        zz = np.linspace(1e-1, 1, 100)
        x, w = gauss_jacobi_pts_wts_1D(200, 0, 0)
        x = (x+1)/2  # map to [0,1]
        quad_rules = [[x, w]]*(nvars-1)
        product_pdf = product_of_independent_random_variables_pdf(
            pdfs[0], quad_rules, zz)

        if nvars == 2:
            true_pdf = -np.log(zz)
        if nvars == 3:
            true_pdf = 0.5*np.log(zz)**2
        # for ii in range(nvars):
        #     plt.plot(zz, pdfs[ii](zz),label=r'$X_%d$'%ii)
        # plt.plot(zz,true_pdf, label='Product')
        # plt.plot(zz,product_pdf, '--', label='True Product')
        # plt.legend()
        # plt.show()
        # print(np.linalg.norm(true_pdf-product_pdf,ord=np.inf))
        assert np.linalg.norm(true_pdf-product_pdf, ord=np.inf) < 0.03

    def test_sum_of_independent_uniform_variables(self):
        nvars = 2
        lb1, ub1 = [0, 2]
        lb2, ub2 = [10, 13]
        pdfs = [stats.uniform(lb1, ub1-lb1).pdf]

        # transfomation not defined at 0
        zz = np.linspace(lb1+lb2, ub1+ub2, 100)
        x, w = gauss_jacobi_pts_wts_1D(200, 0, 0)
        x = (x+1)/2*(ub2-lb2)+lb2  # map to [lb2,ub2]
        quad_rules = [[x, w]]
        product_pdf = sum_of_independent_random_variables_pdf(
            pdfs[0], quad_rules, zz)

        true_pdf = partial(sum_two_uniform_variables, [lb1, ub1, lb2, ub2])
        #plt.plot(zz,true_pdf(zz), label='True PDF')
        #plt.plot(zz,product_pdf, '--', label='Approx PDF')
        # nsamples=10000
        #vals = np.random.uniform(lb1,ub1,nsamples)+np.random.uniform(
        #    lb2,ub2,nsamples)
        # plt.hist(vals,bins=100,density=True)
        # plt.legend();plt.show()
        # print(np.linalg.norm(true_pdf-product_pdf,ord=np.inf))
        assert np.linalg.norm(true_pdf(zz)-product_pdf, ord=np.inf) < 0.03


if __name__ == "__main__":
    random_variable_algebra_test_suite = \
        unittest.TestLoader().loadTestsFromTestCase(TestRandomVariableAlgebra)
    unittest.TextTestRunner(verbosity=2).run(
        random_variable_algebra_test_suite)

# nosetests --nocapture --nologcapture ~/software/pyapprox/pyapprox/tests/test_random_variable_algebra.py:TestRandomVariableAlgebra.test_sum_of_independent_uniform_and_gaussian_variables
