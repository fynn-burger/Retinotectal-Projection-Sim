import unittest
from model.growth_cone import GrowthCone


class TestGrowthCone(unittest.TestCase):
    def setUp(self):
        self.growth_cone = GrowthCone((0, 0), 5, 0.5, 0.5, 123)

    def test_str_method(self):
        expected_str = (f"Receptor: {self.growth_cone.receptor_current}, Ligand: {self.growth_cone.ligand_current}, "
                        f"Position: {self.growth_cone.pos}, Start Position: {self.growth_cone.pos_start}, "
                        f"Potential: {self.growth_cone.potential}, ID: {self.growth_cone.id}, "
                        f"Adaptation Coefficient: {self.growth_cone.adap_co}, "
                        f"Reset Forces: {self.growth_cone.reset_force_ligand}, {self.growth_cone.reset_force_receptor}")
        self.assertEqual(str(self.growth_cone), expected_str)

    def test_take_step(self):
        new_potential = 20
        new_position = (1, 1)
        self.growth_cone.pos_new = new_position
        self.growth_cone.take_step(new_potential)
        self.assertEqual(self.growth_cone.potential, new_potential)
        self.assertEqual(self.growth_cone.pos, new_position)

    def test_calculate_adaptation(self):
        mu = 0.5
        lambda_ = 0.3
        h = 5
        self.growth_cone.calculate_adaptation(mu, lambda_, h)
        # Test the values of adap_co, reset_force_receptor, and reset_force_ligand
        # This tests may require more specific checks based on the adaptation formula

    def test_apply_adaptation(self):
        self.growth_cone.apply_adaptation()
        # Test the values of ligand_current and receptor_current
        # Ensure they are correctly calculated and rounded
