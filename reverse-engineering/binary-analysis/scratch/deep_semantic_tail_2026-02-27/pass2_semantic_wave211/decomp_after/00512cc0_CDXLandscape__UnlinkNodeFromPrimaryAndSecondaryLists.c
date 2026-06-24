/* address: 0x00512cc0 */
/* name: CDXLandscape__UnlinkNodeFromPrimaryAndSecondaryLists */
/* signature: uint __stdcall CDXLandscape__UnlinkNodeFromPrimaryAndSecondaryLists(uint param_1) */


uint CDXLandscape__UnlinkNodeFromPrimaryAndSecondaryLists(uint param_1)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint local_4;

  uVar3 = param_1;
  local_4 = 0;
  uVar1 = 0;
  for (uVar2 = DAT_00889074; uVar2 != 0; uVar2 = *(uint *)(uVar2 + 4)) {
    if (uVar2 == param_1) {
      if (uVar1 == 0) {
        DAT_00889074 = *(uint *)(param_1 + 4);
      }
      else {
        *(undefined4 *)(uVar1 + 4) = *(undefined4 *)(param_1 + 4);
      }
      local_4 = 1;
    }
    uVar1 = uVar2;
  }
  param_1 = 0;
  uVar1 = 0;
  for (uVar2 = DAT_00889078; uVar2 != 0; uVar2 = *(uint *)(uVar2 + 4)) {
    if (uVar2 == uVar3) {
      if (uVar1 == 0) {
        DAT_00889078 = *(uint *)(uVar3 + 4);
      }
      else {
        *(undefined4 *)(uVar1 + 4) = *(undefined4 *)(uVar3 + 4);
      }
      param_1 = 1;
    }
    uVar1 = uVar2;
  }
  return param_1 | local_4;
}
