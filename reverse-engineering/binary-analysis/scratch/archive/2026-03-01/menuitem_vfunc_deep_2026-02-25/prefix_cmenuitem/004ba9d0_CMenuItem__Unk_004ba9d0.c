/* address: 0x004ba9d0 */
/* name: CMenuItem__Unk_004ba9d0 */
/* signature: int __fastcall CMenuItem__Unk_004ba9d0(void * param_1) */


int __fastcall CMenuItem__Unk_004ba9d0(void *param_1)

{
  int iVar1;

  iVar1 = CUnitAI__Unk_0047ce80((int)param_1);
  if (iVar1 == 0) {
    return 0;
  }
  (**(code **)(*(int *)param_1 + 0x1d4))();
  return 1;
}
