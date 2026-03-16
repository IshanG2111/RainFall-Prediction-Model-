import { useState, useRef, useEffect, useMemo } from 'react';
import { Calendar, ChevronLeft, ChevronRight } from 'lucide-react';

interface DatePickerProps {
  value: string;            // ISO date string YYYY-MM-DD
  onChange: (date: string) => void;
  id?: string;
}

const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

function toISO(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

export default function DatePicker({ value, onChange, id }: DatePickerProps) {
  const selected = useMemo(() => new Date(value + 'T00:00:00'), [value]);
  const [viewYear, setViewYear] = useState(selected.getFullYear());
  const [viewMonth, setViewMonth] = useState(selected.getMonth());
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  // Close on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // When value changes externally, sync the view
  useEffect(() => {
    setViewYear(selected.getFullYear());
    setViewMonth(selected.getMonth());
  }, [selected]);

  const prevMonth = () => {
    if (viewMonth === 0) {
      setViewMonth(11);
      setViewYear(y => y - 1);
    } else {
      setViewMonth(m => m - 1);
    }
  };

  const nextMonth = () => {
    if (viewMonth === 11) {
      setViewMonth(0);
      setViewYear(y => y + 1);
    } else {
      setViewMonth(m => m + 1);
    }
  };

  // Build calendar grid
  const calendarDays = useMemo(() => {
    const firstDay = new Date(viewYear, viewMonth, 1).getDay();
    const daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate();
    const daysInPrevMonth = new Date(viewYear, viewMonth, 0).getDate();

    const cells: { day: number; currentMonth: boolean; date: Date }[] = [];

    // Previous month trailing days
    for (let i = firstDay - 1; i >= 0; i--) {
      const d = daysInPrevMonth - i;
      cells.push({
        day: d,
        currentMonth: false,
        date: new Date(viewYear, viewMonth - 1, d),
      });
    }

    // Current month days
    for (let d = 1; d <= daysInMonth; d++) {
      cells.push({
        day: d,
        currentMonth: true,
        date: new Date(viewYear, viewMonth, d),
      });
    }

    // Next month leading days (fill to 42 cells = 6 rows)
    const remaining = 42 - cells.length;
    for (let d = 1; d <= remaining; d++) {
      cells.push({
        day: d,
        currentMonth: false,
        date: new Date(viewYear, viewMonth + 1, d),
      });
    }

    return cells;
  }, [viewYear, viewMonth]);

  const today = useMemo(() => toISO(new Date()), []);

  const handleSelect = (date: Date) => {
    onChange(toISO(date));
    setOpen(false);
  };

  const formattedDisplay = selected.toLocaleDateString('en-IN', {
    weekday: 'short',
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });

  return (
    <div className="relative" ref={ref}>
      <label className="block text-gray-500 text-xs font-bold mb-2 uppercase tracking-widest">
        Date
      </label>

      {/* Trigger Button */}
      <button
        type="button"
        onClick={() => setOpen(o => !o)}
        className="flex items-center border-b-2 border-gray-900 pb-2 w-full text-left cursor-pointer group"
        id={id}
      >
        <Calendar className="w-5 h-5 mr-3 text-gray-700 group-hover:text-gray-900 transition-colors" strokeWidth={1.5} />
        <span className="text-gray-900 font-bold text-lg flex-1">
          {formattedDisplay}
        </span>
        <ChevronRight
          className={`w-4 h-4 text-gray-400 transition-transform duration-200 ${open ? 'rotate-90' : ''}`}
          strokeWidth={2}
        />
      </button>

      {/* Calendar Dropdown */}
      {open && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-white border-2 border-gray-900 shadow-[4px_4px_0px_0px_#111827] z-[100] select-none">
          {/* Month / Year Header */}
          <div className="flex items-center justify-between px-2 py-1.5 border-b-2 border-gray-900 bg-gray-50">
            <button
              type="button"
              onClick={prevMonth}
              className="p-0.5 hover:bg-gray-200 transition-colors cursor-pointer"
              aria-label="Previous month"
            >
              <ChevronLeft className="w-3.5 h-3.5 text-gray-900" strokeWidth={2.5} />
            </button>
            <span className="font-hand text-base font-bold text-gray-900 tracking-wide">
              {MONTHS[viewMonth]} {viewYear}
            </span>
            <button
              type="button"
              onClick={nextMonth}
              className="p-0.5 hover:bg-gray-200 transition-colors cursor-pointer"
              aria-label="Next month"
            >
              <ChevronRight className="w-3.5 h-3.5 text-gray-900" strokeWidth={2.5} />
            </button>
          </div>

          {/* Day-of-week headers */}
          <div className="grid grid-cols-7 border-b border-gray-200">
            {DAYS.map((d) => (
              <div
                key={d}
                className="text-center text-[9px] font-bold text-gray-400 uppercase tracking-wider py-1"
              >
                {d}
              </div>
            ))}
          </div>

          {/* Day cells */}
          <div className="grid grid-cols-7 px-0.5 py-0.5">
            {calendarDays.map((cell, idx) => {
              const iso = toISO(cell.date);
              const isSelected = iso === value;
              const isToday = iso === today;

              return (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSelect(cell.date)}
                  className={`
                    relative w-full h-7 flex items-center justify-center
                    text-[11px] font-bold transition-all duration-100 cursor-pointer
                    ${!cell.currentMonth
                      ? 'text-gray-300'
                      : isSelected
                        ? 'bg-gray-900 text-white shadow-[2px_2px_0px_0px_#374151]'
                        : 'text-gray-900 hover:bg-gray-100'
                    }
                    ${isToday && !isSelected
                      ? 'ring-2 ring-inset ring-gray-900'
                      : ''
                    }
                  `}
                >
                  {cell.day}
                </button>
              );
            })}
          </div>

          {/* Footer — Today Shortcut */}
          <div className="border-t-2 border-gray-900 px-2 py-1.5 flex justify-between items-center bg-gray-50">
            <span className="text-[9px] text-gray-400 font-bold uppercase tracking-widest">
              // Pick a date
            </span>
            <button
              type="button"
              onClick={() => handleSelect(new Date())}
              className="text-[9px] font-bold text-gray-900 uppercase tracking-widest hover:underline cursor-pointer"
            >
              Today
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
