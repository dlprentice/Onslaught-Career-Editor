/* address: 0x00569dd5 */
/* name: CRT__IsFdCommitMode */
/* signature: int __cdecl CRT__IsFdCommitMode(uint param_1) */


int __cdecl CRT__IsFdCommitMode(uint param_1)

{
  if (DAT_009d33a0 <= param_1) {
    return 0;
  }
  return *(byte *)((&DAT_009d32a0)[(int)param_1 >> 5] + 4 + (param_1 & 0x1f) * 0x24) & 0x40;
}
