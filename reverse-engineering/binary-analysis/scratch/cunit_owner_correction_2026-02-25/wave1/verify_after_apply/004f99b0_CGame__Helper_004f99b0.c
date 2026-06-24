/* address: 0x004f99b0 */
/* name: CGame__Helper_004f99b0 */
/* signature: void __fastcall CGame__Helper_004f99b0(int param_1) */


void __fastcall CGame__Helper_004f99b0(int param_1)

{
  void *pvVar1;

  if ((*(int *)(param_1 + 0x164) != 0) &&
     (pvVar1 = *(void **)(*(int *)(param_1 + 0x164) + 0x34), pvVar1 != (void *)0x0)) {
    CSoundManager__Unk_004e1940(&DAT_00896988,pvVar1,(void *)param_1);
  }
  return;
}
