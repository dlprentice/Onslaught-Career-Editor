/* address: 0x0055e183 */
/* name: CFastVB__Unk_0055e183 */
/* signature: int __cdecl CFastVB__Unk_0055e183(int param_1) */


int __cdecl CFastVB__Unk_0055e183(int param_1)

{
  int iVar1;
  int iVar2;

  CRT__LockRouteByIndex(1,0x6533e0);
  iVar1 = CFastVB__Helper_0056381b(&DAT_006533e0);
  iVar2 = CDXTexture__Helper_00561834(0x6533e0,(void *)param_1,&stack0x00000008);
  CFastVB__Helper_005638a8(iVar1,&DAT_006533e0);
  CRT__UnlockRouteByIndex(1,0x6533e0);
  return iVar2;
}
