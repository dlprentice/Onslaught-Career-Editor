/* address: 0x00441b10 */
/* name: CGame__SetGlobalSelectionSnapshot */
/* signature: void __cdecl CGame__SetGlobalSelectionSnapshot(void * selection_vec4, int selection_mode) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl CGame__SetGlobalSelectionSnapshot(void *selection_vec4,int selection_mode)

{
  if (selection_vec4 != (void *)0x0) {
    _DAT_0066eb80 = *(undefined4 *)selection_vec4;
    DAT_0066eb84 = *(undefined4 *)((int)selection_vec4 + 4);
    _DAT_0066eb88 = *(undefined4 *)((int)selection_vec4 + 8);
    _DAT_0066eb8c = *(undefined4 *)((int)selection_vec4 + 0xc);
    DAT_0066ff74 = 1;
    DAT_0066ff75 = (undefined1)selection_mode;
    return;
  }
  DAT_0066eb84 = 0xffffffff;
  _DAT_0066eb80 = 0;
  DAT_0066ff74 = 1;
  DAT_0066ff75 = (undefined1)selection_mode;
  return;
}
