/* address: 0x0056745c */
/* name: CRT__SbHeapResizeChunkInRegion_0056745c */
/* signature: int __cdecl CRT__SbHeapResizeChunkInRegion_0056745c(int param_1, void * param_2, void * param_3, uint param_4) */


int __cdecl
CRT__SbHeapResizeChunkInRegion_0056745c(int param_1,void *param_2,void *param_3,uint param_4)

{
  char *pcVar1;
  int *piVar2;
  char cVar3;
  char *pcVar4;
  int iVar5;
  uint uVar6;

  uVar6 = (uint)*(byte *)param_3;
  piVar2 = (int *)(param_1 + 0x18 + ((int)param_2 - *(int *)(param_1 + 0x10) >> 0xc) * 8);
  if (param_4 < uVar6) {
    *(undefined1 *)param_3 = (undefined1)param_4;
    *piVar2 = *piVar2 + (uVar6 - param_4);
    piVar2[1] = 0xf1;
  }
  else {
    if (param_4 <= uVar6) {
      return 0;
    }
    pcVar1 = (char *)((int)param_3 + param_4);
    if ((char *)((int)param_2 + 0xf8U) < pcVar1) {
      return 0;
    }
    for (pcVar4 = (char *)(uVar6 + (int)param_3); (pcVar4 < pcVar1 && (*pcVar4 == '\0'));
        pcVar4 = pcVar4 + 1) {
    }
    if (pcVar4 != pcVar1) {
      return 0;
    }
    *(undefined1 *)param_3 = (undefined1)param_4;
    if ((param_3 <= *(char **)param_2) && (*(char **)param_2 < pcVar1)) {
      if (pcVar1 < (char *)((int)param_2 + 0xf8U)) {
        iVar5 = 0;
        *(char **)param_2 = pcVar1;
        cVar3 = *pcVar1;
        while (cVar3 == '\0') {
          iVar5 = iVar5 + 1;
          cVar3 = pcVar1[iVar5];
        }
        *(int *)((int)param_2 + 4) = iVar5;
      }
      else {
        *(undefined4 *)((int)param_2 + 4) = 0;
        *(int *)param_2 = (int)param_2 + 8;
      }
    }
    *piVar2 = *piVar2 + (uVar6 - param_4);
  }
  return 1;
}
