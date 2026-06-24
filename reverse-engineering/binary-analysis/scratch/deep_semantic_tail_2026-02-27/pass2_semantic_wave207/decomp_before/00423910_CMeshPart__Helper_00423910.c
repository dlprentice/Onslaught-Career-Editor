/* address: 0x00423910 */
/* name: CMeshPart__Helper_00423910 */
/* signature: uint __fastcall CMeshPart__Helper_00423910(uint param_1) */


uint __fastcall CMeshPart__Helper_00423910(uint param_1)

{
  int iVar1;
  uint local_4;

  *(undefined4 *)(param_1 + 8) = 0;
  local_4 = param_1;
  iVar1 = DXMemBuffer__ReadBytes(&local_4,4);
  if (iVar1 < 4) {
    return 0;
  }
  iVar1 = DXMemBuffer__ReadBytes(param_1,4);
  return local_4 & (iVar1 < 4) - 1;
}
