/* address: 0x004d3630 */
/* name: CEngine__Unk_004d3630 */
/* signature: void __fastcall CEngine__Unk_004d3630(void * param_1) */


void __fastcall CEngine__Unk_004d3630(void *param_1)

{
  float10 fVar1;

  CUnit__Unk_004fa8d0(param_1);
  fVar1 = (float10)(**(code **)(*(int *)param_1 + 0xb4))();
  *(float *)((int)param_1 + 0x84) = (float)(fVar1 + (float10)*(float *)((int)param_1 + 0x84));
  return;
}
