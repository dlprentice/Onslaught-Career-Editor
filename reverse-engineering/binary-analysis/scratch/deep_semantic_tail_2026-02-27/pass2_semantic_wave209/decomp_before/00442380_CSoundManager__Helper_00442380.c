/* address: 0x00442380 */
/* name: CSoundManager__Helper_00442380 */
/* signature: void __fastcall CSoundManager__Helper_00442380(void * param_1) */


void __fastcall CSoundManager__Helper_00442380(void *param_1)

{
  int *piVar1;
  int *piVar2;

  piVar2 = DAT_0066ffb0;
  if (DAT_0066ffb0 == param_1) {
    DAT_0066ffb0 = (int *)*(undefined4 *)param_1;
    return;
  }
  do {
    piVar1 = piVar2;
    if (piVar1 == (int *)0x0) break;
    piVar2 = (int *)*piVar1;
  } while ((int *)*piVar1 != param_1);
  *piVar1 = *(int *)param_1;
  return;
}
