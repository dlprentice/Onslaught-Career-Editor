/* address: 0x0044d1f0 */
/* name: CUnitAI__Unk_0044d1f0 */
/* signature: void __fastcall CUnitAI__Unk_0044d1f0(void * param_1) */


void __fastcall CUnitAI__Unk_0044d1f0(void *param_1)

{
  CUnitAI__Helper_00402000((int)param_1);
  if ((*(byte *)((int)param_1 + 0x2c) & 4) != 0) {
    (**(code **)(*(int *)param_1 + 0x38))();
  }
  return;
}
