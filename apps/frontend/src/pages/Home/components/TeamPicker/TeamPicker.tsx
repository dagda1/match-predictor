import Autocomplete from '@mui/material/Autocomplete';
import Skeleton from '@mui/material/Skeleton';
import TextField from '@mui/material/TextField';

interface TeamPickerProps {
  label: string;
  value: string | null;
  onChange: (value: string | null) => void;
  options: string[];
  exclude: string | null;
  loading?: boolean;
}

export function TeamPicker({ label, value, onChange, options, exclude, loading }: Readonly<TeamPickerProps>): JSX.Element {
  if (loading) {
    return <Skeleton variant="rounded" height={56} width="100%" animation="wave" />;
  }

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
