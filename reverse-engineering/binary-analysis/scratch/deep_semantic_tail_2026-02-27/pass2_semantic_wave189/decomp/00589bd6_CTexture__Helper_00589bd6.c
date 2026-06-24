/* address: 0x00589bd6 */
/* name: CTexture__Helper_00589bd6 */
/* signature: void __cdecl CTexture__Helper_00589bd6(int param_1, void * param_2) */


void __cdecl CTexture__Helper_00589bd6(int param_1,void *param_2)

{
  int iVar1;
  void *unaff_EBX;
  char *pcVar2;
  char *pcVar3;
  bool bVar4;
  undefined1 local_104 [255];
  undefined1 local_5;

  *(undefined4 *)(param_1 + 0x2c) = 1;
  if (*(int *)(param_1 + 0x38) != 0) {
    iVar1 = 0xd;
    bVar4 = true;
    pcVar2 = param_2;
    pcVar3 = "syntax error";
    do {
      if (iVar1 == 0) break;
      iVar1 = iVar1 + -1;
      bVar4 = *pcVar2 == *pcVar3;
      pcVar2 = pcVar2 + 1;
      pcVar3 = pcVar3 + 1;
    } while (bVar4);
    if (bVar4) {
      if ((*(int *)(param_1 + 0x34) == 0) || (*(int *)(param_1 + 0x60) != 9)) {
        CTexture__LogUnexpectedTokenError_0058cabd
                  ((void *)(param_1 + 4),(void *)0x5dc,param_1 + 0x60,unaff_EBX);
      }
      else {
        CTexture__Helper_0058c893((void *)(param_1 + 4),param_1 + 0x60,0x5e0,0x5ea390);
      }
    }
    else {
      CRT__VsnprintfAndTerminate_005d070f(local_104,0x100,param_2,&stack0x0000000c);
      local_5 = 0;
      CTexture__Helper_0058c893((void *)(param_1 + 4),param_1 + 0x60,0,0x5ea38c);
    }
  }
  return;
}
