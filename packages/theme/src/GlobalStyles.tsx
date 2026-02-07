import MUIGlobalStyles from '@mui/material/GlobalStyles';

const globalStyle = {
  ['html,body']: {
    height: '100%',
  },
  body: {
    display: 'flex',
    flexDirection: 'column',
  },
  ['#root']: {
    display: 'flex',
    flexDirection: 'column',
    flex: 1,
    minHeight: 0,
    minWidth: 0,
  },
  img: {
    maxWidth: '100%',
  },
  ul: {
    margin: 0,
    padding: 0,
    listStyle: 'none',
  },
  ['*,*:before,*:after']: {
    boxSizing: 'border-box',
  },
} as const;

export function GlobalStyles(): JSX.Element {
  return <MUIGlobalStyles styles={globalStyle} />;
}
