/* address: 0x004048f0 */
/* name: CMesh__IsValidProfileIndex_1to10 */
/* signature: int __cdecl CMesh__IsValidProfileIndex_1to10(int param_1) */


int __cdecl CMesh__IsValidProfileIndex_1to10(int param_1)

{
  if ((0 < param_1) && (param_1 < 0xb)) {
    return 1;
  }
  return 0;
}
