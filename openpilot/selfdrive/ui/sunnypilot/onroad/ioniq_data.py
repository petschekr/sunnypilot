import pyray as rl

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.selfdrive.ui.onroad.hud_renderer import FONT_SIZES, COLORS

class IoniqData:
  def __init__(self):
    self._font_bold: rl.Font = gui_app.font(FontWeight.BOLD)
    self._font_medium: rl.Font = gui_app.font(FontWeight.MEDIUM)

    self.altitude: float = 0.0
    self.power: float = 0.0
    self.current: float = 0.0

    self.energySinceIgnition: float = 0.0
    self.energySinceCharging: float = 0.0

    self.maxChargePower: float = 0.0
    self.maxDischargePower: float = 0.0
    self.maxRequestedChargeCurrent: float = 0.0
    self.maxRequestedChargePower: float = 0.0
    self.minBatteryTemp: int = 0
    self.maxBatteryTemp: int = 0
    self.batteryInletTemp: int = 0
    self.heaterTemp: int = 0
    self.sunrise: str = "--:--"
    self.sunset: str = "--:--"
    self.acChargeSessionDuration = "--:--"
    self.dcChargeSessionDuration = "--:--"

    self.brakeLight = False

  def update(self):
    sm = ui_state.sm
    ioniq_state = sm['ioniq']

    self.altitude = ioniq_state.altitudeMsl
    self.power = ioniq_state.voltage * ioniq_state.current / 1000.0
    self.current = ioniq_state.current

    self.energySinceIgnition = ioniq_state.energySinceIgnition / 1000.0
    self.energySinceCharging = ioniq_state.energySinceCharging / 1000.0
    self.acChargeSessionDuration = ioniq_state.acChargeSessionDuration
    self.dcChargeSessionDuration = ioniq_state.dcChargeSessionDuration

    self.maxChargePower = ioniq_state.availableChargePower
    self.maxDischargePower = ioniq_state.availableDischargePower
    self.maxRequestedChargeCurrent = ioniq_state.maximumChargeCurrent
    self.maxRequestedChargePower = ioniq_state.maximumChargePower
    self.minBatteryTemp = ioniq_state.minBatteryTemp
    self.maxBatteryTemp = ioniq_state.maxBatteryTemp
    self.batteryInletTemp = ioniq_state.batteryInletTemp
    self.heaterTemp = ioniq_state.heaterTemp

    self.sunrise = ioniq_state.sunrise
    self.sunset = ioniq_state.sunset

    self.brakeLight = ioniq_state.brakeLight

  def render(self, rect: rl.Rectangle, sm) -> None:
    self._draw_power(rect)
    self._draw_energy(rect)
    self._draw_altitude(rect)
    if self.maxChargePower > 0:
      self._draw_requested_power(rect)
      self._draw_requested_current(rect)
      self._draw_session_time(rect)

    if self.brakeLight:
      self._draw_brake_line(rect)

    self._draw_sun_times(rect)

  def _draw_statistic(self, rect: rl.Rectangle, label: str, text: str, x: int, y: int) -> None:
    label_size = measure_text_cached(self._font_medium, label, 60)
    label_pos = rl.Vector2(rect.x + x - label_size.x / 2, rect.height - y - label_size.y / 2)
    rl.draw_text_ex(self._font_medium, label, label_pos, 60, 0, COLORS.WHITE_TRANSLUCENT)

    text_size = measure_text_cached(self._font_bold, text, 70)
    text_pos = rl.Vector2(rect.x + x - text_size.x / 2, rect.height - (y - 75) - text_size.y / 2)
    rl.draw_text_ex(self._font_bold, text, text_pos, 70, 0, COLORS.WHITE)

  def _draw_power(self, rect: rl.Rectangle) -> None:
    """Draw the current power consumed from the battery in kW"""
    text = str(round(self.power, 1)) + " kW"
    self._draw_statistic(rect, "Power", text, 175, 445)

  def _draw_requested_power(self, rect: rl.Rectangle) -> None:
    """Draw the requested charge power in kW"""
    text = str(round(self.maxRequestedChargePower)) + " kW"
    self._draw_statistic(rect, "Requested Power", text, 650, 445)

  def _draw_energy(self, rect: rl.Rectangle) -> None:
    """Draw the energy consumed since ignition start in kWh"""
    text = str(round(self.energySinceIgnition, 1)) + " kWh"
    self._draw_statistic(rect, "Energy", text, 175, 285)

  def _draw_requested_current(self, rect: rl.Rectangle) -> None:
    """Draw the requested charge current in A"""
    text = str(round(self.current)) + "/" + str(round(self.maxRequestedChargeCurrent)) + " A"
    self._draw_statistic(rect, "Charge Current", text, 650, 285)

  def _draw_altitude(self, rect: rl.Rectangle) -> None:
    """Draw the GPS altitude MSL"""
    text = str(round(self.altitude * 3.28084)) + " ft"
    self._draw_statistic(rect, "Altitude", text, 175, 125)

  def _draw_session_time(self, rect: rl.Rectangle) -> None:
    """Draw the pre-computed charge session time string"""
    if self.acChargeSessionDuration:
      self._draw_statistic(rect, "AC Session", self.acChargeSessionDuration, 650, 125)
    if self.dcChargeSessionDuration:
      self._draw_statistic(rect, "DC Session", self.dcChargeSessionDuration, 650, 125)

  def _draw_sun_times(self, rect: rl.Rectangle) -> None:
    text_size = measure_text_cached(self._font_bold, self.sunrise, 20)
    text_pos = rl.Vector2(rect.x + rect.width - 200 - text_size.x / 2, rect.y + 90 - text_size.y / 2)
    rl.draw_text_ex(self._font_bold, self.sunrise, text_pos, 70, 0, COLORS.WHITE_TRANSLUCENT)

    text_size = measure_text_cached(self._font_bold, self.sunset, 20)
    text_pos = rl.Vector2(rect.x + rect.width - 200 - text_size.x / 2, rect.y + 155 - text_size.y / 2)
    rl.draw_text_ex(self._font_bold, self.sunset, text_pos, 70, 0, COLORS.WHITE_TRANSLUCENT)

  def _draw_brake_line(self, rect: rl.Rectangle) -> None:
    start = rl.Vector2(rect.x + 350, rect.y + rect.height - 35)
    end =   rl.Vector2(rect.x + rect.width - 350, rect.y + rect.height - 35)
    thickness = 35.0
    rl.draw_line_ex(
      start, end,
      thickness,
      rl.Color(235, 32, 32, 255)
    )
    rl.draw_circle_v(
      start,
      thickness / 2.0,
      rl.Color(235, 32, 32, 255)
    )
    rl.draw_circle_v(
      end,
      thickness / 2.0,
      rl.Color(235, 32, 32, 255)
    )
