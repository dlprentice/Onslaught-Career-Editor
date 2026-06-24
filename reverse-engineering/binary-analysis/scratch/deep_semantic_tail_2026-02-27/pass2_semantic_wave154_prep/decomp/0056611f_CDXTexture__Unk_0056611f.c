/* address: 0x0056611f */
/* name: CDXTexture__Unk_0056611f */
/* signature: void __cdecl CDXTexture__Unk_0056611f(void * param_1) */


void __cdecl CDXTexture__Unk_0056611f(void *param_1)

{
  int iVar1;
  HMODULE pHVar2;

  *(undefined4 *)param_1 = 0;
  pHVar2 = GetModuleHandleA((LPCSTR)0x0);
  if (((short)pHVar2->unused == 0x5a4d) && (iVar1 = pHVar2[0xf].unused, iVar1 != 0)) {
    *(undefined1 *)param_1 = *(undefined1 *)((int)&pHVar2[6].unused + iVar1 + 2);
    *(undefined1 *)((int)param_1 + 1) = *(undefined1 *)((int)&pHVar2[6].unused + iVar1 + 3);
  }
  return;
}
