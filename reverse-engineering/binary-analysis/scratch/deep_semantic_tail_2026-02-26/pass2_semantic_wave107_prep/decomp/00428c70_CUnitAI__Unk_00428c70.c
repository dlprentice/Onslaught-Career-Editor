/* address: 0x00428c70 */
/* name: CUnitAI__Unk_00428c70 */
/* signature: void __fastcall CUnitAI__Unk_00428c70(void * param_1) */


void __fastcall CUnitAI__Unk_00428c70(void *param_1)

{
  CUnit__Helper_00402010((int)param_1);
  if ((*(byte *)((int)param_1 + 0x2c) & 4) != 0) {
    (**(code **)(*(int *)param_1 + 0x38))();
  }
  return;
}
