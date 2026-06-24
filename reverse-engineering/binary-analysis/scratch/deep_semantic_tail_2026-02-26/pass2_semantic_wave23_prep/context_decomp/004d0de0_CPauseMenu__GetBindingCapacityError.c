/* address: 0x004d0de0 */
/* name: CPauseMenu__GetBindingCapacityError */
/* signature: int CPauseMenu__GetBindingCapacityError(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CPauseMenu__GetBindingCapacityError(void)

{
  uint uVar1;
  wchar_t *pwVar2;
  int iVar3;

  uVar1 = Controls__FindFirstFreeBindingSlot(0);
  if ((char)uVar1 == '\0') {
    pwVar2 = Localization__GetStringById(0xe8);
    return (int)pwVar2;
  }
  if ((0 < DAT_008a9ac0) && (DAT_008a9ac0 < 9)) {
    iVar3 = CExplosionInitThing__Helper_004725d0(0x8a9a98);
    if (iVar3 != 0) {
      uVar1 = Controls__FindFirstFreeBindingSlot(1);
      if ((char)uVar1 == '\0') {
        pwVar2 = Localization__GetStringById(0xe9);
        return (int)pwVar2;
      }
    }
  }
  return 0;
}
