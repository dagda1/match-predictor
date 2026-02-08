import Autocomplete from '@mui/material/Autocomplete';
import TextField from '@mui/material/TextField';

interface TeamPickerProps {
  label: string;
  value: string | null;
  onChange: (value: string | null) => void;
  options: string[];
  exclude: string | null;
}

export function TeamPicker({ label, value, onChange, options, exclude }: TeamPickerProps): JSX.Element {
  const filtered = options.filter((t) => t !== exclude);

  return (
    <Autocomplete
      value={value}
      onChange={(_, v) => onChange(v)}
      options={filtered}
      freeSolo={false}
      renderInput={(params) => <TextField {...params} label={label} variant="outlined" />}
      disableClearable={false}
      fullWidth
    />
  );
}
