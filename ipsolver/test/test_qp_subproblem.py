import numpy as np
from scipy.sparse import csc_matrix
from ipsolver import (eqp_kktfact, projections, projected_cg, orthogonality,
                      box_boundaries_intersections,
                      spherical_boundaries_intersections,
                      box_sphere_boundaries_intersections,
                      modified_dogleg)
from numpy.testing import (TestCase, assert_array_almost_equal,
                           assert_array_equal, assert_array_less,
                           assert_raises, assert_equal, assert_,
                           run_module_suite, assert_allclose, assert_warns,
                           dec)


class TestEQPDirectFactorization(TestCase):

    # From Example 16.2 Nocedal/Wright "Numerical
    # Optimization" p.452
    def test_nocedal_example(self):

        H = csc_matrix([[6, 2, 1],
                        [2, 5, 2],
                        [1, 2, 4]])
        A = csc_matrix([[1, 0, 1],
                        [0, 1, 1]])
        c = np.array([-8, -3, -3])
        b = np.array([3, 0])

        x, lagrange_multipliers = eqp_kktfact(H, c, A, b)

        assert_array_almost_equal(x, [2, -1, 1])
        assert_array_almost_equal(lagrange_multipliers, [3, -2])


class TestSphericalBoundariesIntersections(TestCase):

    def test_2d_sphere_constraints(self):

        # Interior inicial point
        ta, tb, intersect = spherical_boundaries_intersections([0, 0],
                                                               [1, 0], 0.5)
        assert_array_almost_equal([ta, tb], [0, 0.5])
        assert_equal(intersect, True)

        # No intersection between line and circle
        ta, tb, intersect = spherical_boundaries_intersections([2, 0],
                                                               [0, 1], 1)
        assert_equal(intersect, False)

        # Outside inicial point pointing toward outside the circle
        ta, tb, intersect = spherical_boundaries_intersections([2, 0],
                                                               [1, 0], 1)
        assert_equal(intersect, False)

        # Outside inicial point pointing toward inside the circle
        ta, tb, intersect = spherical_boundaries_intersections([2, 0],
                                                               [-1, 0], 1.5)
        assert_array_almost_equal([ta, tb], [0.5, 1])
        assert_equal(intersect, True)

        # Inicial point on the boundary
        ta, tb, intersect = spherical_boundaries_intersections([2, 0],
                                                               [1, 0], 2)
        assert_array_almost_equal([ta, tb], [0, 0])
        assert_equal(intersect, True)

    def test_2d_sphere_constraints_line_intersections(self):

        # Interior inicial point
        ta, tb, intersect = spherical_boundaries_intersections([0, 0],
                                                               [1, 0], 0.5,
                                                               line_intersections=True)
        assert_array_almost_equal([ta, tb], [-0.5, 0.5])
        assert_equal(intersect, True)

        # No intersection between line and circle
        ta, tb, intersect = spherical_boundaries_intersections([2, 0],
                                                               [0, 1], 1,
                                                               line_intersections=True)
        assert_equal(intersect, False)

        # Outside inicial point pointing toward outside the circle
        ta, tb, intersect = spherical_boundaries_intersections([2, 0],
                                                               [1, 0], 1,
                                                               line_intersections=True)
        assert_array_almost_equal([ta, tb], [-3, -1])
        assert_equal(intersect, True)

        # Outside inicial point pointing toward inside the circle
        ta, tb, intersect = spherical_boundaries_intersections([2, 0],
                                                               [-1, 0], 1.5,
                                                               line_intersections=True)
        assert_array_almost_equal([ta, tb], [0.5, 3.5])
        assert_equal(intersect, True)

        # Inicial point on the boundary
        ta, tb, intersect = spherical_boundaries_intersections([2, 0],
                                                               [1, 0], 2,
                                                               line_intersections=True)
        assert_array_almost_equal([ta, tb], [-4, 0])
        assert_equal(intersect, True)


class TestBoxBoundariesIntersections(TestCase):

    def test_2d_box_constraints(self):

        # Box constraint in the direction of vector d
        ta, tb, intersect = box_boundaries_intersections([2, 0], [0, 2],
                                                         [1, 1], [3, 3])
        assert_array_almost_equal([ta, tb], [0.5, 1])
        assert_equal(intersect, True)

        # Negative direction
        ta, tb, intersect = box_boundaries_intersections([2, 0], [0, 2],
                                                         [1, -3], [3, -1])
        assert_equal(intersect, False)

        # Some constraints are absent (set to +/- inf)
        ta, tb, intersect = box_boundaries_intersections([2, 0], [0, 2],
                                                         [-np.inf, 1],
                                                         [np.inf, np.inf])
        assert_array_almost_equal([ta, tb], [0.5, 1])
        assert_equal(intersect, True)

        # Intersect on the face of the box
        ta, tb, intersect = box_boundaries_intersections([1, 0], [0, 1],
                                                         [1, 1], [3, 3])
        assert_array_almost_equal([ta, tb], [1, 1])
        assert_equal(intersect, True)

        # Interior inicial pointoint
        ta, tb, intersect = box_boundaries_intersections([0, 0], [4, 4],
                                                         [-2, -3], [3, 2])
        assert_array_almost_equal([ta, tb], [0, 0.5])
        assert_equal(intersect, True)

        # No intersection between line and box constraints
        ta, tb, intersect = box_boundaries_intersections([2, 0], [0, 2],
                                                         [-3, -3], [-1, -1])
        assert_equal(intersect, False)
        ta, tb, intersect = box_boundaries_intersections([2, 0], [0, 2],
                                                         [-3, 3], [-1, 1])
        assert_equal(intersect, False)
        ta, tb, intersect = box_boundaries_intersections([2, 0], [0, 2],
                                                         [-3, -np.inf],
                                                         [-1, np.inf])
        assert_equal(intersect, False)
        ta, tb, intersect = box_boundaries_intersections([0, 0], [1, 100],
                                                         [1, 1], [3, 3])
        assert_equal(intersect, False)
        ta, tb, intersect = box_boundaries_intersections([0.99, 0], [0, 2],
                                                         [1, 1], [3, 3])
        assert_equal(intersect, False)

        # Inicial point on the boundary
        ta, tb, intersect = box_boundaries_intersections([2, 2], [0, 1],
                                                         [-2, -2], [2, 2])
        assert_array_almost_equal([ta, tb], [0, 0])
        assert_equal(intersect, True)

    def test_2d_box_constraints_line_intersections(self):

        # Box constraint in the direction of vector d
        ta, tb, intersect = box_boundaries_intersections([2, 0], [0, 2],
                                                         [1, 1], [3, 3],
                                                         line_intersections=True)
        assert_array_almost_equal([ta, tb], [0.5, 1.5])
        assert_equal(intersect, True)

        # Negative direction
        ta, tb, intersect = box_boundaries_intersections([2, 0], [0, 2],
                                                         [1, -3], [3, -1],
                                                         line_intersections=True)
        assert_array_almost_equal([ta, tb], [-1.5, -0.5])
        assert_equal(intersect, True)

        # Some constraints are absent (set to +/- inf)
        ta, tb, intersect = box_boundaries_intersections([2, 0], [0, 2],
                                                         [-np.inf, 1],
                                                         [np.inf, np.inf],
                                                         line_intersections=True)
        assert_array_almost_equal([ta, tb], [0.5, np.inf])
        assert_equal(intersect, True)

        # Intersect on the face of the box
        ta, tb, intersect = box_boundaries_intersections([1, 0], [0, 1],
                                                         [1, 1], [3, 3],
                                                         line_intersections=True)
        assert_array_almost_equal([ta, tb], [1, 3])
        assert_equal(intersect, True)

        # Interior inicial pointoint
        ta, tb, intersect = box_boundaries_intersections([0, 0], [4, 4],
                                                         [-2, -3], [3, 2],
                                                         line_intersections=True)
        assert_array_almost_equal([ta, tb], [-0.5, 0.5])
        assert_equal(intersect, True)

        # No intersection between line and box constraints
        ta, tb, intersect = box_boundaries_intersections([2, 0], [0, 2],
                                                         [-3, -3], [-1, -1],
                                                         line_intersections=True)
        assert_equal(intersect, False)
        ta, tb, intersect = box_boundaries_intersections([2, 0], [0, 2],
                                                         [-3, 3], [-1, 1],
                                                         line_intersections=True)
        assert_equal(intersect, False)
        ta, tb, intersect = box_boundaries_intersections([2, 0], [0, 2],
                                                         [-3, -np.inf],
                                                         [-1, np.inf],
                                                         line_intersections=True)
        assert_equal(intersect, False)
        ta, tb, intersect = box_boundaries_intersections([0, 0], [1, 100],
                                                         [1, 1], [3, 3],
                                                         line_intersections=True)
        assert_equal(intersect, False)
        ta, tb, intersect = box_boundaries_intersections([0.99, 0], [0, 2],
                                                         [1, 1], [3, 3],
                                                         line_intersections=True)
        assert_equal(intersect, False)

        # Inicial point on the boundary
        ta, tb, intersect = box_boundaries_intersections([2, 2], [0, 1],
                                                         [-2, -2], [2, 2],
                                                         line_intersections=True)
        assert_array_almost_equal([ta, tb], [-4, 0])
        assert_equal(intersect, True)

    def test_3d_box_constraints(self):

        # Simple case
        ta, tb, intersect = box_boundaries_intersections([1, 1, 0], [0, 0, 1],
                                                         [1, 1, 1], [3, 3, 3])
        assert_array_almost_equal([ta, tb], [1, 1])
        assert_equal(intersect, True)

        # Negative direction
        ta, tb, intersect = box_boundaries_intersections([1, 1, 0], [0, 0, -1],
                                                         [1, 1, 1], [3, 3, 3])
        assert_equal(intersect, False)

        # Interior Point
        ta, tb, intersect = box_boundaries_intersections([2, 2, 2], [0, -1, 1],
                                                         [1, 1, 1], [3, 3, 3])
        assert_array_almost_equal([ta, tb], [0, 1])
        assert_equal(intersect, True)

    def test_3d_box_constraints_line_intersections(self):

        # Simple case
        ta, tb, intersect = box_boundaries_intersections([1, 1, 0], [0, 0, 1],
                                                         [1, 1, 1], [3, 3, 3],
                                                         line_intersections=True)
        assert_array_almost_equal([ta, tb], [1, 3])
        assert_equal(intersect, True)

        # Negative direction
        ta, tb, intersect = box_boundaries_intersections([1, 1, 0], [0, 0, -1],
                                                         [1, 1, 1], [3, 3, 3],
                                                         line_intersections=True)
        assert_array_almost_equal([ta, tb], [-3, -1])
        assert_equal(intersect, True)

        # Interior Point
        ta, tb, intersect = box_boundaries_intersections([2, 2, 2], [0, -1, 1],
                                                         [1, 1, 1], [3, 3, 3],
                                                         line_intersections=True)
        assert_array_almost_equal([ta, tb], [-1, 1])
        assert_equal(intersect, True)


class TestBoxSphereBoundariesIntersections(TestCase):

    def test_2d_box_constraints(self):

        # Both constraints are active
        ta, tb, intersect = box_sphere_boundaries_intersections([1, 1], [-2, 2],
                                                                [-1, -2], [1, 2], 2,
                                                                line_intersections=False)
        assert_array_almost_equal([ta, tb], [0, 0.5])
        assert_equal(intersect, True)

        # None of the contraints are active
        ta, tb, intersect = box_sphere_boundaries_intersections([1, 1], [-1, 1],
                                                                [-1, -3], [1, 3], 10,
                                                                line_intersections=False)
        assert_array_almost_equal([ta, tb], [0, 1])
        assert_equal(intersect, True)

        # Box Constraints are active
        ta, tb, intersect = box_sphere_boundaries_intersections([1, 1], [-4, 4],
                                                                [-1, -3], [1, 3], 10,
                                                                line_intersections=False)
        assert_array_almost_equal([ta, tb], [0, 0.5])
        assert_equal(intersect, True)

        # Spherical Constraints are active
        ta, tb, intersect = box_sphere_boundaries_intersections([1, 1], [-4, 4],
                                                                [-1, -3], [1, 3], 2,
                                                                line_intersections=False)
        assert_array_almost_equal([ta, tb], [0, 0.25])
        assert_equal(intersect, True)

        # Infeasible problems
        ta, tb, intersect = box_sphere_boundaries_intersections([2, 2], [-4, 4],
                                                                [-1, -3], [1, 3], 2,
                                                                line_intersections=False)
        assert_equal(intersect, False)
        ta, tb, intersect = box_sphere_boundaries_intersections([1, 1], [-4, 4],
                                                                [2, 4], [2, 4], 2,
                                                                line_intersections=False)
        assert_equal(intersect, False)

    def test_2d_box_constraints_line_intersections(self):

        # Both constraints are active
        ta, tb, intersect = box_sphere_boundaries_intersections([1, 1], [-2, 2],
                                                                [-1, -2], [1, 2], 2,
                                                                line_intersections=True)
        assert_array_almost_equal([ta, tb], [0, 0.5])
        assert_equal(intersect, True)

        # None of the contraints are active
        ta, tb, intersect = box_sphere_boundaries_intersections([1, 1], [-1, 1],
                                                                [-1, -3], [1, 3], 10,
                                                                line_intersections=True)
        assert_array_almost_equal([ta, tb], [0, 2])
        assert_equal(intersect, True)

        # Box Constraints are active
        ta, tb, intersect = box_sphere_boundaries_intersections([1, 1], [-4, 4],
                                                                [-1, -3], [1, 3], 10,
                                                                line_intersections=True)
        assert_array_almost_equal([ta, tb], [0, 0.5])
        assert_equal(intersect, True)

        # Spherical Constraints are active
        ta, tb, intersect = box_sphere_boundaries_intersections([1, 1], [-4, 4],
                                                                [-1, -3], [1, 3], 2,
                                                                line_intersections=True)
        assert_array_almost_equal([ta, tb], [0, 0.25])
        assert_equal(intersect, True)

        # Infeasible problems
        ta, tb, intersect = box_sphere_boundaries_intersections([2, 2], [-4, 4],
                                                                [-1, -3], [1, 3], 2,
                                                                line_intersections=True)
        assert_equal(intersect, False)
        ta, tb, intersect = box_sphere_boundaries_intersections([1, 1], [-4, 4],
                                                                [2, 4], [2, 4], 2,
                                                                line_intersections=True)
        assert_equal(intersect, False)


class TestModifiedDogleg(TestCase):

    def test_cauchypoint_equalsto_newtonpoint(self):

        A = np.array([[1, 8]])
        b = np.array([-16])
        _, _, Y = projections(A)

        newton_point = np.array([ 0.24615385,  1.96923077])
        cauchy_point = newton_point
        origin = np.zeros_like(newton_point)

        # Newton point inside boundaries:
        x = modified_dogleg(A, Y, b, 2, [-np.inf, -np.inf], [np.inf, np.inf])
        assert_array_almost_equal(x, newton_point)

        # Spherical constraint active
        x = modified_dogleg(A, Y, b, 1, [-np.inf, -np.inf], [np.inf, np.inf])
        assert_array_almost_equal(x, newton_point / np.linalg.norm(newton_point))

        # Box Constraints active
        x = modified_dogleg(A, Y, b, 2, [-np.inf, -np.inf], [0.1, np.inf])
        assert_array_almost_equal(x, (newton_point/newton_point[0]) * 0.1)

    def test_3d_example(self):

        A = np.array([[1, 8, 1],
                      [4, 2, 2]])
        b = np.array([-16, 2])
        Z, LS, Y = projections(A)

        newton_point = np.array([-1.37090909, 2.23272727, -0.49090909])
        cauchy_point = np.array([ 0.11165723, 1.73068711, 0.16748585])
        origin = np.zeros_like(newton_point)

        # newton_point inside boundaries:
        x = modified_dogleg(A, Y, b, 3, [-np.inf, -np.inf, -np.inf],
                            [np.inf, np.inf, np.inf])
        assert_array_almost_equal(x, newton_point)

        # line between cauchy_point and newton_point contains best point
        # (spherical constrain is active)
        x = modified_dogleg(A, Y, b, 2, [-np.inf, -np.inf, -np.inf],
                            [np.inf, np.inf, np.inf])
        z = cauchy_point
        d = newton_point-cauchy_point
        t = ((x-z)/(d))
        assert_array_almost_equal(t, 0.40807330*np.ones(3))
        assert_array_almost_equal(np.linalg.norm(x), 2)

        # line between cauchy_point and newton_point contains best point
        # (box constrain is active)
        x = modified_dogleg(A, Y, b, 5, [-1, -np.inf, -np.inf],
                            [np.inf, np.inf, np.inf])
        z = cauchy_point
        d = newton_point-cauchy_point
        t = ((x-z)/(d))
        assert_array_almost_equal(t, 0.7498195*np.ones(3))
        assert_array_almost_equal(x[0], -1)

        # line between origin and cauchy_point contains best point
        # (spherical constrain is active)
        x = modified_dogleg(A, Y, b, 1, [-np.inf, -np.inf, -np.inf],
                            [np.inf, np.inf, np.inf])
        z = origin
        d = cauchy_point
        t = ((x-z)/(d))
        assert_array_almost_equal(t, 0.573936265*np.ones(3))
        assert_array_almost_equal(np.linalg.norm(x), 1)

        # line between origin and newton_point contains best point
        # (box constrain is active)
        x = modified_dogleg(A, Y, b, 2, [-np.inf, -np.inf, -np.inf],
                            [np.inf, 1, np.inf])
        z = origin
        d = newton_point
        t = ((x-z)/(d))
        assert_array_almost_equal(t, 0.4478827364*np.ones(3))
        assert_array_almost_equal(x[1], 1)

class TestProjections(TestCase):

    def test_nullspace_and_least_squares_sparse(self):
        A_dense = np.array([[1, 2, 3, 4, 0, 5, 0, 7],
                            [0, 8, 7, 0, 1, 5, 9, 0],
                            [1, 0, 0, 0, 0, 1, 2, 3]])
        At_dense = A_dense.T
        A = csc_matrix(A_dense)

        test_points = ([1, 2, 3, 4, 5, 6, 7, 8],
                       [1, 10, 3, 0, 1, 6, 7, 8],
                       [1.12, 10, 0, 0, 100000, 6, 0.7, 8])

        for method in ("NormalEquation", "AugmentedSystem"):
            Z, LS, _ = projections(A, method)

            for z in test_points:
                # Test if x is in the null_space
                x = Z.matvec(z)
                assert_array_almost_equal(A.dot(x), 0)

                # Test orthogonality
                assert_array_almost_equal(orthogonality(A, x), 0)

                # Test if x is the least square solution
                x = LS.matvec(z)
                x2 = np.linalg.lstsq(At_dense, z)[0]
                assert_array_almost_equal(x, x2)

    def test_iterative_refinements_sparse(self):
        A_dense = np.array([[1, 2, 3, 4, 0, 5, 0, 7],
                            [0, 8, 7, 0, 1, 5, 9, 0],
                            [1, 0, 0, 0, 0, 1, 2, 3]])
        At_dense = A_dense.T
        A = csc_matrix(A_dense)

        test_points = ([1, 2, 3, 4, 5, 6, 7, 8],
                       [1, 10, 3, 0, 1, 6, 7, 8],
                       [1.12, 10, 0, 0, 100000, 6, 0.7, 8],
                       [1, 0, 0, 0, 0, 1, 2, 3+1e-10])

        for method in ("NormalEquation", "AugmentedSystem"):
            Z, LS, _ = projections(A, method, orth_tol=1e-18, max_refin=100)

            for z in test_points:
                # Test if x is in the null_space
                x = Z.matvec(z)
                assert_array_almost_equal(A.dot(x), 0, decimal=14)

                # Test orthogonality
                assert_array_almost_equal(orthogonality(A, x), 0, decimal=16)

    def test_rowspace_sparse(self):

        A_dense = np.array([[1, 2, 3, 4, 0, 5, 0, 7],
                            [0, 8, 7, 0, 1, 5, 9, 0],
                            [1, 0, 0, 0, 0, 1, 2, 3]])
        At_dense = A_dense.T
        A = csc_matrix(A_dense)

        test_points = ([1, 2, 3],
                       [1, 10, 3],
                       [1.12, 10, 0])

        for method in ('NormalEquation', 'AugmentedSystem'):
            _, _, Y = projections(A, method)

            for z in test_points:
                # Test if x is solution of A x = z
                x = Y.matvec(z)
                assert_array_almost_equal(A.dot(x), z)

                # Test if x is in the return row space of A
                A_ext = np.vstack((A_dense, x))
                assert_equal(np.linalg.matrix_rank(A_dense),
                             np.linalg.matrix_rank(A_ext))

    def test_nullspace_and_least_squares_dense(self):
        A = np.array([[1, 2, 3, 4, 0, 5, 0, 7],
                      [0, 8, 7, 0, 1, 5, 9, 0],
                      [1, 0, 0, 0, 0, 1, 2, 3]])
        At = A.T

        test_points = ([1, 2, 3, 4, 5, 6, 7, 8],
                       [1, 10, 3, 0, 1, 6, 7, 8],
                       [1.12, 10, 0, 0, 100000, 6, 0.7, 8])

        for method in ("QRFactorization",):
            Z, LS, _ = projections(A, method)

            for z in test_points:
                # Test if x is in the null_space
                x = Z.matvec(z)
                assert_array_almost_equal(A.dot(x), 0)

                # Test orthogonality
                assert_array_almost_equal(orthogonality(A, x), 0)

                # Test if x is the least square solution
                x = LS.matvec(z)
                x2 = np.linalg.lstsq(At, z)[0]
                assert_array_almost_equal(x, x2)

    def test_iterative_refinements_dense(self):
        A = np.array([[1, 2, 3, 4, 0, 5, 0, 7],
                            [0, 8, 7, 0, 1, 5, 9, 0],
                            [1, 0, 0, 0, 0, 1, 2, 3]])

        test_points = ([1, 2, 3, 4, 5, 6, 7, 8],
                       [1, 10, 3, 0, 1, 6, 7, 8],
                       [1, 0, 0, 0, 0, 1, 2, 3+1e-10])

        for method in ("QRFactorization",):
            Z, LS, _ = projections(A, method, orth_tol=1e-18, max_refin=10)

            for z in test_points:
                # Test if x is in the null_space
                x = Z.matvec(z)
                assert_array_almost_equal(A.dot(x), 0, decimal=14)

                # Test orthogonality
                assert_array_almost_equal(orthogonality(A, x), 0, decimal=16)

    def test_rowspace_dense(self):

        A = np.array([[1, 2, 3, 4, 0, 5, 0, 7],
                      [0, 8, 7, 0, 1, 5, 9, 0],
                      [1, 0, 0, 0, 0, 1, 2, 3]])

        test_points = ([1, 2, 3],
                       [1, 10, 3],
                       [1.12, 10, 0])

        for method in ('QRFactorization',):
            _, _, Y = projections(A, method)

            for z in test_points:
                # Test if x is solution of A x = z
                x = Y.matvec(z)
                assert_array_almost_equal(A.dot(x), z)

                # Test if x is in the return row space of A
                A_ext = np.vstack((A, x))
                assert_equal(np.linalg.matrix_rank(A),
                             np.linalg.matrix_rank(A_ext))


class TestOrthogonality(TestCase):

    def test_dense_matrix(self):

        A = np.array([[1, 2, 3, 4, 0, 5, 0, 7],
                      [0, 8, 7, 0, 1, 5, 9, 0],
                      [1, 0, 0, 0, 0, 1, 2, 3]])

        test_vectors = ([-1.98931144, -1.56363389,
                         -0.84115584, 2.2864762,
                         5.599141, 0.09286976,
                         1.37040802, -0.28145812],
                        [697.92794044, -4091.65114008,
                         -3327.42316335, 836.86906951,
                         99434.98929065, -1285.37653682,
                         -4109.21503806,   2935.29289083])

        test_expected_orth = (0, 0)

        for i in range(len(test_vectors)):
            x = test_vectors[i]
            orth = test_expected_orth[i]

            assert_array_almost_equal(orthogonality(A, x), orth)

    def test_sparse_matrix(self):

        A = np.array([[1, 2, 3, 4, 0, 5, 0, 7],
                      [0, 8, 7, 0, 1, 5, 9, 0],
                      [1, 0, 0, 0, 0, 1, 2, 3]])
        A = csc_matrix(A)

        test_vectors = ([-1.98931144, -1.56363389,
                         -0.84115584, 2.2864762,
                         5.599141, 0.09286976,
                         1.37040802, -0.28145812],
                        [697.92794044, -4091.65114008,
                         -3327.42316335, 836.86906951,
                         99434.98929065, -1285.37653682,
                         -4109.21503806,   2935.29289083])

        test_expected_orth = (0, 0)

        for i in range(len(test_vectors)):
            x = test_vectors[i]
            orth = test_expected_orth[i]

            assert_array_almost_equal(orthogonality(A, x), orth)


class TestProjectCG(TestCase):

    # From Example 16.2 Nocedal/Wright "Numerical
    # Optimization" p.452
    def test_nocedal_example(self):

        H = csc_matrix([[6, 2, 1],
                        [2, 5, 2],
                        [1, 2, 4]])
        A = csc_matrix([[1, 0, 1],
                        [0, 1, 1]])
        c = np.array([-8, -3, -3])
        b = np.array([3, 0])

        Z, _, Y = projections(A)

        x, hits_boundary, info = projected_cg(H, c, Z, Y, b)

        assert_equal(info["stop_cond"], 4)
        assert_equal(hits_boundary, False)
        assert_array_almost_equal(x, [2, -1, 1])

    def test_compare_with_direct_fact(self):

        H = csc_matrix([[6, 2, 1, 3],
                        [2, 5, 2, 4],
                        [1, 2, 4, 5],
                        [3, 4, 5, 7]])
        A = csc_matrix([[1, 0, 1, 0],
                        [0, 1, 1, 1]])
        c = np.array([-2, -3, -3, 1])
        b = np.array([3, 0])

        Z, _, Y = projections(A)

        x, hits_boundary, info = projected_cg(H, c, Z, Y, b, tol=0)
        x_kkt, _ = eqp_kktfact(H, c, A, b)

        assert_equal(info["stop_cond"], 1)
        assert_equal(hits_boundary, False)
        assert_array_almost_equal(x, x_kkt)

    def test_trust_region_infeasible(self):

        H = csc_matrix([[6, 2, 1, 3],
                        [2, 5, 2, 4],
                        [1, 2, 4, 5],
                        [3, 4, 5, 7]])
        A = csc_matrix([[1, 0, 1, 0],
                        [0, 1, 1, 1]])
        c = np.array([-2, -3, -3, 1])
        b = np.array([3, 0])

        trust_radius = 1

        Z, _, Y = projections(A)

        assert_raises(ValueError, projected_cg, H, c,
                      Z, Y, b, trust_radius=trust_radius)

    def test_trust_region_barely_feasible(self):

        H = csc_matrix([[6, 2, 1, 3],
                        [2, 5, 2, 4],
                        [1, 2, 4, 5],
                        [3, 4, 5, 7]])
        A = csc_matrix([[1, 0, 1, 0],
                        [0, 1, 1, 1]])
        c = np.array([-2, -3, -3, 1])
        b = np.array([3, 0])

        trust_radius = 2.32379000772445021283

        Z, _, Y = projections(A)

        x, hits_boundary, info = projected_cg(H, c, Z, Y, b,
                                              tol=0,
                                              trust_radius=trust_radius)

        assert_equal(info["stop_cond"], 2)
        assert_equal(hits_boundary, True)
        assert_array_almost_equal(np.linalg.norm(x), trust_radius)
        assert_array_almost_equal(x, Y.dot(b))

    def test_hits_boundary(self):

        H = csc_matrix([[6, 2, 1, 3],
                        [2, 5, 2, 4],
                        [1, 2, 4, 5],
                        [3, 4, 5, 7]])
        A = csc_matrix([[1, 0, 1, 0],
                        [0, 1, 1, 1]])
        c = np.array([-2, -3, -3, 1])
        b = np.array([3, 0])

        trust_radius = 3

        Z, _, Y = projections(A)

        x, hits_boundary, info = projected_cg(H, c, Z, Y, b,
                                              tol=0,
                                              trust_radius=trust_radius)

        assert_equal(info["stop_cond"], 2)
        assert_equal(hits_boundary, True)
        assert_array_almost_equal(np.linalg.norm(x), trust_radius)

    def test_negative_curvature_unconstrained(self):

        H = csc_matrix([[1, 2, 1, 3],
                        [2, 0, 2, 4],
                        [1, 2, 0, 2],
                        [3, 4, 2, 0]])
        A = csc_matrix([[1, 0, 1, 0],
                        [0, 1, 0, 1]])
        c = np.array([-2, -3, -3, 1])
        b = np.array([3, 0])

        Z, _, Y = projections(A)

        assert_raises(ValueError, projected_cg, H, c, Z, Y, b, tol=0)

    def test_negative_curvature(self):

        H = csc_matrix([[1, 2, 1, 3],
                        [2, 0, 2, 4],
                        [1, 2, 0, 2],
                        [3, 4, 2, 0]])
        A = csc_matrix([[1, 0, 1, 0],
                        [0, 1, 0, 1]])
        c = np.array([-2, -3, -3, 1])
        b = np.array([3, 0])

        Z, _, Y = projections(A)

        trust_radius = 1000

        x, hits_boundary, info = projected_cg(H, c, Z, Y, b,
                                              tol=0,
                                              trust_radius=trust_radius)

        assert_equal(info["stop_cond"], 3)
        assert_equal(hits_boundary, True)
        assert_array_almost_equal(np.linalg.norm(x), trust_radius)

    # The box contraints are inactive at the solution but
    # are active during the iterations
    def test_inactive_box_constraints(self):

        H = csc_matrix([[6, 2, 1, 3],
                        [2, 5, 2, 4],
                        [1, 2, 4, 5],
                        [3, 4, 5, 7]])
        A = csc_matrix([[1, 0, 1, 0],
                        [0, 1, 1, 1]])
        c = np.array([-2, -3, -3, 1])
        b = np.array([3, 0])

        Z, _, Y = projections(A)

        x, hits_boundary, info = projected_cg(H, c, Z, Y, b,
                                              tol=0,
                                              lb=[0.5, -np.inf,
                                                  -np.inf, -np.inf],
                                              return_all=True)
        x_kkt, _ = eqp_kktfact(H, c, A, b)

        assert_equal(info["stop_cond"], 1)
        assert_equal(hits_boundary, False)
        assert_array_almost_equal(x, x_kkt)

    # The box contraints active and the termination is
    # by maximum iterations (infeasible iteraction)
    def test_active_box_constraints_maximum_iterations_reached(self):

        H = csc_matrix([[6, 2, 1, 3],
                        [2, 5, 2, 4],
                        [1, 2, 4, 5],
                        [3, 4, 5, 7]])
        A = csc_matrix([[1, 0, 1, 0],
                        [0, 1, 1, 1]])
        c = np.array([-2, -3, -3, 1])
        b = np.array([3, 0])

        Z, _, Y = projections(A)

        x, hits_boundary, info = projected_cg(H, c, Z, Y, b,
                                              tol=0,
                                              lb=[0.8, -np.inf,
                                                  -np.inf, -np.inf],
                                              return_all=True)

        assert_equal(info["stop_cond"], 1)
        assert_equal(hits_boundary, True)
        assert_array_almost_equal(A.dot(x), b)
        assert_array_almost_equal(x[0], 0.8)

    # The box contraints are active and the termination is
    # because it hits boundary (without infeasible iteraction)
    def test_active_box_constraints_hits_boundaries(self):

        H = csc_matrix([[6, 2, 1, 3],
                        [2, 5, 2, 4],
                        [1, 2, 4, 5],
                        [3, 4, 5, 7]])
        A = csc_matrix([[1, 0, 1, 0],
                        [0, 1, 1, 1]])
        c = np.array([-2, -3, -3, 1])
        b = np.array([3, 0])

        trust_radius = 3

        Z, _, Y = projections(A)

        x, hits_boundary, info = projected_cg(H, c, Z, Y, b,
                                              tol=0,
                                              ub=[np.inf, np.inf, 1.6, np.inf],
                                              trust_radius=trust_radius,
                                              return_all=True)

        assert_equal(info["stop_cond"], 2)
        assert_equal(hits_boundary, True)
        assert_array_almost_equal(x[2], 1.6)

    # The box contraints are active and the termination is
    # because it hits boundary (infeasible iteraction)
    def test_active_box_constraints_hits_boundaries_infeasible_iter(self):

        H = csc_matrix([[6, 2, 1, 3],
                        [2, 5, 2, 4],
                        [1, 2, 4, 5],
                        [3, 4, 5, 7]])
        A = csc_matrix([[1, 0, 1, 0],
                        [0, 1, 1, 1]])
        c = np.array([-2, -3, -3, 1])
        b = np.array([3, 0])

        trust_radius = 4

        Z, _, Y = projections(A)

        x, hits_boundary, info = projected_cg(H, c, Z, Y, b,
                                              tol=0,
                                              ub=[np.inf, 0.1, np.inf, np.inf],
                                              trust_radius=trust_radius,
                                              return_all=True)

        assert_equal(info["stop_cond"], 2)
        assert_equal(hits_boundary, True)
        assert_array_almost_equal(x[1], 0.1)

    # The box contraints are active and the termination is
    # because it hits boundary (no infeasible iteraction)
    def test_active_box_constraints_negative_curvature(self):

        H = csc_matrix([[1, 2, 1, 3],
                        [2, 0, 2, 4],
                        [1, 2, 0, 2],
                        [3, 4, 2, 0]])
        A = csc_matrix([[1, 0, 1, 0],
                        [0, 1, 0, 1]])
        c = np.array([-2, -3, -3, 1])
        b = np.array([3, 0])

        Z, _, Y = projections(A)

        trust_radius = 1000

        x, hits_boundary, info = projected_cg(H, c, Z, Y, b,
                                              tol=0,
                                              ub=[np.inf, np.inf, 100, np.inf],
                                              trust_radius=trust_radius)

        assert_equal(info["stop_cond"], 3)
        assert_equal(hits_boundary, True)
        assert_array_almost_equal(x[2], 100)
