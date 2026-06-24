/* address: 0x004080f0 */
/* name: CGame__Unk_004080f0 */
/* signature: int __fastcall CGame__Unk_004080f0(void * param_1) */


int __fastcall CGame__Unk_004080f0(void *param_1)

{
  int iVar1;

  if (*(int *)((int)param_1 + 0x260) != 2) {
    return 0;
  }
  iVar1 = (**(code **)(*(int *)param_1 + 0x10c))();
  if ((iVar1 == 0) && (iVar1 = HeightDelta__Below015_D4((int)param_1), iVar1 == 0)) {
    return 0;
  }
  return 1;
}
