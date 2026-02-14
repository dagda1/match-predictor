import type dayjs from 'dayjs';

export const ISO_DATE_FORMAT = 'YYYY-MM-DD';
export const DISPLAY_DATE_FORMAT = 'D MMM';

export function mondayForDate(d: dayjs.Dayjs): dayjs.Dayjs {
  const day = d.day();
  const daysFromMonday = day === 0 ? 6 : day - 1;
  return d.subtract(daysFromMonday, 'day');
}
