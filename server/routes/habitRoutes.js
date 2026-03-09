const express = require('express');
const router = express.Router();
const authMiddleware = require('../middleware/authMiddleware');
const {
  getHabits,
  addHabit,
  deleteHabit,
  completeHabit,
  getProgress,
} = require('../controllers/habitController');

// All habit routes are protected
router.use(authMiddleware);

router.get('/progress', getProgress);
router.get('/', getHabits);
router.post('/', addHabit);
router.delete('/:id', deleteHabit);
router.post('/:id/complete', completeHabit);

module.exports = router;
