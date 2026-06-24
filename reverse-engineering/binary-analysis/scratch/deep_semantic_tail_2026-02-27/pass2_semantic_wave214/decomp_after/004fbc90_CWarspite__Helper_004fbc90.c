/* address: 0x004fbc90 */
/* name: CWarspite__Helper_004fbc90 */
/* signature: double __fastcall CWarspite__Helper_004fbc90(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CWarspite__Helper_004fbc90(int param_1)

{
  if (*(int *)(param_1 + 0x140) != 0) {
    return (double)*(float *)(*(int *)(*(int *)(param_1 + 0x140) + 0xa0) + 0x88);
  }
  return (double)_DAT_005d856c;
}
