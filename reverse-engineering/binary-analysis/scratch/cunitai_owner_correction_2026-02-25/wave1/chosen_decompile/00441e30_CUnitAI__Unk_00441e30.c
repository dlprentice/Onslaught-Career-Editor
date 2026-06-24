/* address: 0x00441e30 */
/* name: CUnitAI__Unk_00441e30 */
/* signature: int __fastcall CUnitAI__Unk_00441e30(void * param_1) */


int __fastcall CUnitAI__Unk_00441e30(void *param_1)

{
  undefined1 uVar1;
  undefined4 in_EAX;

  uVar1 = *(undefined1 *)param_1;
  *(undefined1 *)param_1 = 1;
  return CONCAT31((int3)((uint)in_EAX >> 8),uVar1);
}
