/* address: 0x00566996 */
/* name: CTexture__Unk_00566996 */
/* signature: int CTexture__Unk_00566996(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__Unk_00566996(void)

{
  undefined4 *puVar1;
  LPVOID pvVar2;

  if (DAT_009d35d8 == DAT_009d35c8) {
    pvVar2 = HeapReAlloc(DAT_009d35e4,0,DAT_009d35dc,(DAT_009d35c8 * 5 + 0x50) * 4);
    if (pvVar2 == (LPVOID)0x0) {
      return 0;
    }
    DAT_009d35c8 = DAT_009d35c8 + 0x10;
    DAT_009d35dc = pvVar2;
  }
  puVar1 = (undefined4 *)((int)DAT_009d35dc + DAT_009d35d8 * 0x14);
  pvVar2 = HeapAlloc(DAT_009d35e4,8,0x41c4);
  puVar1[4] = pvVar2;
  if (pvVar2 != (LPVOID)0x0) {
    pvVar2 = VirtualAlloc((LPVOID)0x0,0x100000,0x2000,4);
    puVar1[3] = pvVar2;
    if (pvVar2 != (LPVOID)0x0) {
      puVar1[2] = 0xffffffff;
      *puVar1 = 0;
      puVar1[1] = 0;
      DAT_009d35d8 = DAT_009d35d8 + 1;
      *(undefined4 *)puVar1[4] = 0xffffffff;
      return (int)puVar1;
    }
    HeapFree(DAT_009d35e4,0,(LPVOID)puVar1[4]);
  }
  return 0;
}
