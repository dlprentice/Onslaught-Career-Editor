/* address: 0x00544060 */
/* name: CDXEngine__Unk_00544060 */
/* signature: void __fastcall CDXEngine__Unk_00544060(void * param_1) */


void __fastcall CDXEngine__Unk_00544060(void *param_1)

{
  int iVar1;

  iVar1 = 5;
  do {
    if (*(int *)param_1 != 0) {
      CHud__Helper_004f27e0(*(int *)param_1 + 8);
      *(int *)param_1 = 0;
    }
    param_1 = (void *)((int)param_1 + 4);
    iVar1 = iVar1 + -1;
  } while (iVar1 != 0);
  if (DAT_008aa908 != (undefined4 *)0x0) {
    (**(code **)*DAT_008aa908)(1);
    DAT_008aa908 = (undefined4 *)0x0;
  }
  return;
}
