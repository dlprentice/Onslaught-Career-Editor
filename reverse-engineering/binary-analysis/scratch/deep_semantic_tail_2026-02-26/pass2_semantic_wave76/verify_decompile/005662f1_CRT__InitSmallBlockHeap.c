/* address: 0x005662f1 */
/* name: CRT__InitSmallBlockHeap */
/* signature: int __cdecl CRT__InitSmallBlockHeap(int param_1) */


int __cdecl CRT__InitSmallBlockHeap(int param_1)

{
  DAT_009d35dc = HeapAlloc(DAT_009d35e4,0,0x140);
  if (DAT_009d35dc == (LPVOID)0x0) {
    return 0;
  }
  DAT_009d35d4 = 0;
  DAT_009d35d8 = 0;
  DAT_009d35d0 = DAT_009d35dc;
  DAT_009d35e0 = param_1;
  DAT_009d35c8 = 0x10;
  return 1;
}
