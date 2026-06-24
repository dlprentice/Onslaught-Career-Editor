/* address: 0x00566fd2 */
/* name: CDXTexture__Helper_00566fd2 */
/* signature: void __cdecl CDXTexture__Helper_00566fd2(int param_1) */


void __cdecl CDXTexture__Helper_00566fd2(int param_1)

{
  BOOL BVar1;
  int *piVar2;
  int iVar3;
  undefined *puVar4;
  undefined *puVar5;
  int local_8;

  puVar4 = PTR_LOOP_00653d84;
  do {
    puVar5 = puVar4;
    if (*(int *)(puVar4 + 0x10) != -1) {
      local_8 = 0;
      piVar2 = (int *)(puVar4 + 0x2010);
      iVar3 = 0x3ff000;
      do {
        if (*piVar2 == 0xf0) {
          BVar1 = VirtualFree((LPVOID)(iVar3 + *(int *)(puVar4 + 0x10)),0x1000,0x4000);
          if (BVar1 != 0) {
            *piVar2 = -1;
            DAT_009d09bc = DAT_009d09bc + -1;
            if ((*(int **)(puVar4 + 0xc) == (int *)0x0) || (piVar2 < *(int **)(puVar4 + 0xc))) {
              *(int **)(puVar4 + 0xc) = piVar2;
            }
            local_8 = local_8 + 1;
            param_1 = param_1 + -1;
            if (param_1 == 0) break;
          }
        }
        iVar3 = iVar3 + -0x1000;
        piVar2 = piVar2 + -2;
      } while (-1 < iVar3);
      puVar5 = *(undefined **)(puVar4 + 4);
      if ((local_8 != 0) && (*(int *)(puVar4 + 0x18) == -1)) {
        piVar2 = (int *)(puVar4 + 0x20);
        iVar3 = 1;
        do {
          if (*piVar2 != -1) break;
          iVar3 = iVar3 + 1;
          piVar2 = piVar2 + 2;
        } while (iVar3 < 0x400);
        if (iVar3 == 0x400) {
          CDXTexture__Helper_00566f7c(puVar4);
        }
      }
    }
    if ((puVar5 == PTR_LOOP_00653d84) || (puVar4 = puVar5, param_1 < 1)) {
      return;
    }
  } while( true );
}
