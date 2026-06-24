/* address: 0x00527e00 */
/* name: CWaterRenderSystem__Helper_00527e00 */
/* signature: uint __fastcall CWaterRenderSystem__Helper_00527e00(int param_1) */


uint __fastcall CWaterRenderSystem__Helper_00527e00(int param_1)

{
  if (*(int *)(param_1 + 0x10) != 0) {
    return CONCAT31((int3)((uint)*(int *)(param_1 + 0x10) >> 8),1);
  }
  if (DAT_00854dd8 != '\0') {
    CConsole__Printf(&DAT_0066eb90,s_RM__Failed_CheckVBufValid_on___s_0064bcfc);
    if (*(int *)(param_1 + 0xc) == 0) {
      *(undefined4 *)(param_1 + 0x10) = 1;
      return 1;
    }
    *(undefined4 *)(param_1 + 0x10) = 0;
    *(int *)(param_1 + 0xc) = *(int *)(param_1 + 0xc) + -1;
  }
  return (uint)(DAT_00854dd8 == '\0');
}
