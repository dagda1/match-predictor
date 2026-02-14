import type dayjs from 'dayjs';

export const ISO_DATE_FORMAT = 'YYYY-MM-DD';
export const DISPLAY_DATE_FORMAT = 'D MMM';

export function saturdayForDate(d: dayjs.Dayjs): dayjs.Dayjs {
  return d.day() === 6 ? d : d.subtract(d.day() + 1, 'day');
}
