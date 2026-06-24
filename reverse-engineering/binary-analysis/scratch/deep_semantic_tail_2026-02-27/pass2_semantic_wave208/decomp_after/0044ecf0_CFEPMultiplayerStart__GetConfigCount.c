/* address: 0x0044ecf0 */
/* name: CFEPMultiplayerStart__GetConfigCount */
/* signature: int CFEPMultiplayerStart__GetConfigCount(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFEPMultiplayerStart__GetConfigCount(void)

{
  int *piVar1;

  DAT_0089da3c = DAT_0089da34;
  if (DAT_0089da34 == (undefined4 *)0x0) {
    piVar1 = (int *)0x0;
  }
  else {
    piVar1 = (int *)*DAT_0089da34;
  }
  while( true ) {
    if (piVar1 == (int *)0x0) {
      return 0;
    }
    if (DAT_0089d94c == *piVar1) break;
    DAT_0089da3c = (undefined4 *)DAT_0089da3c[1];
    if (DAT_0089da3c == (undefined4 *)0x0) {
      piVar1 = (int *)0x0;
    }
    else {
      piVar1 = (int *)*DAT_0089da3c;
    }
  }
  if (piVar1 == (int *)0x0) {
    return 0;
  }
  DAT_0089da3c = DAT_0089da3c;
  return piVar1[8];
}
