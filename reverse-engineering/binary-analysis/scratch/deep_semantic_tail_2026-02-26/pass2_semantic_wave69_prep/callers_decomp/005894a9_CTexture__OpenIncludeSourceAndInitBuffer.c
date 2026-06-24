/* address: 0x005894a9 */
/* name: CTexture__OpenIncludeSourceAndInitBuffer */
/* signature: int CTexture__OpenIncludeSourceAndInitBuffer(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__OpenIncludeSourceAndInitBuffer(void)

{
  char *pcVar1;
  WCHAR WVar2;
  WCHAR *pWVar3;
  undefined4 *extraout_EAX;
  DWORD nBufferLength;
  int extraout_EAX_00;
  int extraout_EAX_01;
  int iVar4;
  int in_ECX;
  uint uVar5;
  undefined4 *puVar6;
  int unaff_EDI;
  undefined4 *puVar7;
  WCHAR *in_stack_00000004;
  LPSTR in_stack_00000008;
  void *in_stack_0000000c;
  void *in_stack_00000010;
  void *in_stack_00000014;
  undefined4 in_stack_00000018;
  undefined4 in_stack_0000001c;
  WCHAR local_108 [130];

  *(void **)(in_ECX + 0x58) = in_stack_00000014;
  if (in_stack_00000008 != (LPSTR)0x0) {
    WideCharToMultiByte(0xfde9,0,in_stack_00000004,-1,(LPSTR)local_108,0x104,(LPCSTR)0x0,(LPBOOL)0x0
                       );
    in_stack_00000004 = local_108;
  }
  if (in_stack_00000014 == (void *)0x0) {
    nBufferLength = GetFullPathNameA((LPCSTR)in_stack_00000004,0,(LPSTR)0x0,(LPSTR *)0x0);
    in_stack_00000014 = (void *)(nBufferLength + 1);
    CTexture__Helper_0058c107(in_stack_0000000c,in_stack_00000014,unaff_EDI);
    *(int *)(in_ECX + 0x60) = extraout_EAX_00;
    if (extraout_EAX_00 != 0) {
      CTexture__Helper_0058c107(in_stack_0000000c,in_stack_00000014,unaff_EDI);
      *(int *)(in_ECX + 0x5c) = extraout_EAX_01;
      if (extraout_EAX_01 != 0) {
        GetFullPathNameA((LPCSTR)in_stack_00000004,nBufferLength,*(LPSTR *)(in_ECX + 0x60),
                         &stack0x00000008);
        *(undefined1 *)(nBufferLength + *(int *)(in_ECX + 0x60)) = 0;
        puVar6 = *(undefined4 **)(in_ECX + 0x60);
        puVar7 = *(undefined4 **)(in_ECX + 0x5c);
        for (uVar5 = (uint)in_stack_00000014 >> 2; uVar5 != 0; uVar5 = uVar5 - 1) {
          *puVar7 = *puVar6;
          puVar6 = puVar6 + 1;
          puVar7 = puVar7 + 1;
        }
        for (uVar5 = (uint)in_stack_00000014 & 3; uVar5 != 0; uVar5 = uVar5 - 1) {
          *(undefined1 *)puVar7 = *(undefined1 *)puVar6;
          puVar6 = (undefined4 *)((int)puVar6 + 1);
          puVar7 = (undefined4 *)((int)puVar7 + 1);
        }
        if (in_stack_00000008 != (LPSTR)0x0) {
          *in_stack_00000008 = '\0';
        }
        iVar4 = CDXTexture__Unk_0058865c
                          ((void *)(in_ECX + 0x3c),*(void **)(in_ECX + 0x5c),0,unaff_EDI);
        if (iVar4 < 0) {
          CTexture__Helper_0058c893(in_stack_00000010,0,0x5e3,0x5ea300);
          return iVar4;
        }
        *(undefined4 *)(in_ECX + 100) = *(undefined4 *)(in_ECX + 0x44);
        *(undefined4 *)(in_ECX + 0x68) = *(undefined4 *)(in_ECX + 0x48);
        goto LAB_0058962d;
      }
    }
  }
  else {
    pWVar3 = in_stack_00000004;
    do {
      WVar2 = *pWVar3;
      pWVar3 = (WCHAR *)((int)pWVar3 + 1);
    } while ((char)WVar2 != '\0');
    pcVar1 = (char *)((int)pWVar3 + (1 - ((int)in_stack_00000004 + 1)));
    CTexture__Helper_0058c107(in_stack_0000000c,pcVar1,unaff_EDI);
    *(undefined4 **)(in_ECX + 0x5c) = extraout_EAX;
    if (extraout_EAX != (undefined4 *)0x0) {
      puVar6 = extraout_EAX;
      for (uVar5 = (uint)pcVar1 >> 2; uVar5 != 0; uVar5 = uVar5 - 1) {
        *puVar6 = *(undefined4 *)in_stack_00000004;
        in_stack_00000004 = in_stack_00000004 + 2;
        puVar6 = puVar6 + 1;
      }
      for (uVar5 = (uint)pcVar1 & 3; uVar5 != 0; uVar5 = uVar5 - 1) {
        *(char *)puVar6 = (char)*in_stack_00000004;
        in_stack_00000004 = (WCHAR *)((int)in_stack_00000004 + 1);
        puVar6 = (undefined4 *)((int)puVar6 + 1);
      }
      in_stack_00000014 =
           (void *)(**(code **)**(undefined4 **)(in_ECX + 0x58))
                             (*(undefined4 **)(in_ECX + 0x58),in_stack_00000018,
                              *(undefined4 *)(in_ECX + 0x5c),in_stack_0000001c,in_ECX + 100,
                              in_ECX + 0x68);
      if ((int)in_stack_00000014 < 0) {
        CTexture__Helper_0058c893(in_stack_00000010,0,0x5e3,0x5ea300);
        return (int)in_stack_00000014;
      }
LAB_0058962d:
      iVar4 = CMeshCollisionVolume__Helper_0058c396();
      if (iVar4 < 0) {
        return iVar4;
      }
      return 0;
    }
  }
  return -0x7ff8fff2;
}
