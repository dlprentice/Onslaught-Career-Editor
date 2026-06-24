/* address: 0x00566339 */
/* name: CRT__FindSmallBlockHeapEntryForPtr */
/* signature: uint __cdecl CRT__FindSmallBlockHeapEntryForPtr(int param_1) */


uint __cdecl CRT__FindSmallBlockHeapEntryForPtr(int param_1)

{
  uint uVar1;

  uVar1 = DAT_009d35dc;
  while( true ) {
    if (DAT_009d35dc + DAT_009d35d8 * 0x14 <= uVar1) {
      return 0;
    }
    if ((uint)(param_1 - *(int *)(uVar1 + 0xc)) < 0x100000) break;
    uVar1 = uVar1 + 0x14;
  }
  return uVar1;
}
