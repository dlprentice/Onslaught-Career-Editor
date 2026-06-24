/* address: 0x0044eab0 */
/* name: CFEPMultiplayerStart__Helper_0044eab0 */
/* signature: int __cdecl CFEPMultiplayerStart__Helper_0044eab0(int param_1) */


int __cdecl CFEPMultiplayerStart__Helper_0044eab0(int param_1)

{
  undefined4 *puVar1;
  int *piVar2;
  int *piVar3;
  int iVar4;

  DAT_0089da3c = DAT_0089da34;
  if (DAT_0089da34 == (undefined4 *)0x0) {
    piVar3 = (int *)0x0;
  }
  else {
    piVar3 = (int *)*DAT_0089da34;
  }
  while( true ) {
    if (piVar3 == (int *)0x0) {
      return 0;
    }
    if (DAT_0089d94c == *piVar3) break;
    DAT_0089da3c = (undefined4 *)DAT_0089da3c[1];
    if (DAT_0089da3c == (undefined4 *)0x0) {
      piVar3 = (int *)0x0;
    }
    else {
      piVar3 = (int *)*DAT_0089da3c;
    }
  }
  if (piVar3 == (int *)0x0) {
    return 0;
  }
  puVar1 = (undefined4 *)piVar3[5];
  iVar4 = 0;
  piVar3[7] = (int)puVar1;
  if (puVar1 == (undefined4 *)0x0) {
    piVar2 = (int *)0x0;
  }
  else {
    piVar2 = (int *)*puVar1;
  }
  if (piVar2 == (int *)0x0) {
    return 0;
  }
  do {
    if (iVar4 == param_1) {
      return *piVar2;
    }
    iVar4 = iVar4 + 1;
    puVar1 = *(undefined4 **)(piVar3[7] + 4);
    piVar3[7] = (int)puVar1;
    if (puVar1 == (undefined4 *)0x0) {
      piVar2 = (int *)0x0;
    }
    else {
      piVar2 = (int *)*puVar1;
    }
  } while (piVar2 != (int *)0x0);
  return 0;
}
