/* address: 0x00489040 */
/* name: CUnitAI__Unk_00489040 */
/* signature: int __fastcall CUnitAI__Unk_00489040(void * param_1) */


int __fastcall CUnitAI__Unk_00489040(void *param_1)

{
  int iVar1;

  iVar1 = 0;
  if ((((*(int *)((int)param_1 + 0x140) != 0) && (*(int *)((int)param_1 + 0x26c) == 0)) &&
      ((*(byte *)((int)param_1 + 0x2c) & 4) == 0)) &&
     (iVar1 = CUnitAI__Helper_004fc080(param_1), iVar1 != 0)) {
    *(undefined4 *)((int)param_1 + 0x268) = 0x12;
    (**(code **)(*(int *)param_1 + 0xf0))(4,1,0);
  }
  return iVar1;
}
