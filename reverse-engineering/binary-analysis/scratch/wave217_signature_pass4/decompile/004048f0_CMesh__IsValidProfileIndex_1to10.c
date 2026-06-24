/* address: 0x004048f0 */
/* name: CMesh__IsValidProfileIndex_1to10 */
/* signature: int __cdecl CMesh__IsValidProfileIndex_1to10(int profile_index) */


int __cdecl CMesh__IsValidProfileIndex_1to10(int profile_index)

{
  if ((0 < profile_index) && (profile_index < 0xb)) {
    return 1;
  }
  return 0;
}
