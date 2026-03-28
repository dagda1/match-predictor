import { styled } from "@mui/material/styles";

export const Root = styled('div')(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  flex: 1,
  marginLeft: 'auto',
  marginRight: 'auto',
  width: '100%',
  maxWidth: '100%',
  minHeight: 0,
  minWidth: 0,
  [theme.breakpoints.up('xl')]: {
    maxWidth: '91rem',
  },
}));
