/* address: 0x004e66e0 */
/* name: CUnit__Unk_004e66e0 */
/* signature: void __fastcall CUnit__Unk_004e66e0(void * param_1) */


void __fastcall CUnit__Unk_004e66e0(void *param_1)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  float in_stack_ffffffb4;
  float in_stack_ffffffb8;
  float in_stack_ffffffbc;
  float in_stack_ffffffc0;
  float in_stack_ffffffc4;
  float in_stack_ffffffc8;
  float in_stack_ffffffcc;
  float in_stack_ffffffd0;
  float in_stack_ffffffd4;
  float in_stack_ffffffd8;
  float in_stack_ffffffdc;
  float in_stack_ffffffe0;
  float local_10;
  undefined4 local_c;
  undefined4 local_8;
  float local_4;

  local_10 = 0.0;
  puVar2 = &DAT_0083d148;
  puVar3 = (undefined4 *)&stack0xffffffb4;
  for (iVar1 = 0xc; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar3 = *puVar2;
    puVar2 = puVar2 + 1;
    puVar3 = puVar3 + 1;
  }
  local_c = 0;
  local_8 = 0;
  CDXEngine__SetWorldMatrixElements
            (&DAT_009c65c0,local_10,0.0,0.0,local_4,in_stack_ffffffb4,in_stack_ffffffb8,
             in_stack_ffffffbc,in_stack_ffffffc0,in_stack_ffffffc4,in_stack_ffffffc8,
             in_stack_ffffffcc,in_stack_ffffffd0,in_stack_ffffffd4,in_stack_ffffffd8,
             in_stack_ffffffdc,in_stack_ffffffe0);
  (**(code **)(*(int *)param_1 + 0x40))();
  local_10 = *(float *)((int)param_1 + 0x1c);
  local_c = *(undefined4 *)((int)param_1 + 0x20);
  local_8 = *(undefined4 *)((int)param_1 + 0x24);
  local_4 = *(float *)((int)param_1 + 0x28);
  CStaticShadows__Helper_0047eb80(0x6fadc8,&local_10);
  return;
}
