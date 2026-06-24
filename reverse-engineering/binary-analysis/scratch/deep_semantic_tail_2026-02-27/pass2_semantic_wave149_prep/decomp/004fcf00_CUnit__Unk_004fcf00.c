/* address: 0x004fcf00 */
/* name: CUnit__Unk_004fcf00 */
/* signature: void __fastcall CUnit__Unk_004fcf00(int param_1) */


void __fastcall CUnit__Unk_004fcf00(int param_1)

{
  undefined4 local_4;

  *(undefined4 *)(param_1 + 0x14c) = 0;
  *(undefined4 *)(param_1 + 0x150) = 0;
  *(undefined4 *)(param_1 + 0x154) = 0;
  *(undefined4 *)(param_1 + 0x158) = local_4;
  *(undefined4 *)(param_1 + 0x120) = *(undefined4 *)(param_1 + 0x114);
  *(undefined4 *)(param_1 + 0x7c) = 0;
  *(undefined4 *)(param_1 + 0x80) = 0;
  *(undefined4 *)(param_1 + 0x84) = 0;
  *(undefined4 *)(param_1 + 0x88) = local_4;
  if (*(int **)(param_1 + 0x208) != (int *)0x0) {
    (**(code **)(**(int **)(param_1 + 0x208) + 0x20))();
  }
  return;
}
