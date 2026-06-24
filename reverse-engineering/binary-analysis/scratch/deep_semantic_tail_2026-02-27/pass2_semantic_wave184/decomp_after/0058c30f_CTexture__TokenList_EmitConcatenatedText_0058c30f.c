/* address: 0x0058c30f */
/* name: CTexture__TokenList_EmitConcatenatedText_0058c30f */
/* signature: int __thiscall CTexture__TokenList_EmitConcatenatedText_0058c30f(void * this, void * param_1, void * param_2) */


int __thiscall
CTexture__TokenList_EmitConcatenatedText_0058c30f(void *this,void *param_1,void *param_2)

{
  char cVar1;
  undefined4 *puVar2;
  int iVar3;
  char *pcVar4;
  char *pcVar5;
  uint uVar6;
  uint uVar7;
  char *pcVar8;

  if (param_1 != (void *)0x0) {
    if (*(int *)((int)this + 4) == 0) {
      *(undefined4 *)param_1 = 0;
    }
    else {
      iVar3 = CTexture__Helper_00590d3d(*(int *)((int)this + 4) + 1,param_1);
      if (iVar3 < 0) {
        return iVar3;
      }
      iVar3 = (**(code **)(**(int **)param_1 + 0xc))(*(int **)param_1);
      pcVar4 = (char *)(iVar3 + *(int *)((int)this + 4));
      *pcVar4 = '\0';
      for (puVar2 = *(undefined4 **)this; puVar2 != (undefined4 *)0x0;
          puVar2 = (undefined4 *)*puVar2) {
        pcVar5 = (char *)(puVar2 + 1);
        do {
          cVar1 = *pcVar5;
          pcVar5 = pcVar5 + 1;
        } while (cVar1 != '\0');
        uVar6 = (int)pcVar5 - ((int)puVar2 + 5);
        pcVar4 = pcVar4 + -uVar6;
        pcVar5 = (char *)(puVar2 + 1);
        pcVar8 = pcVar4;
        for (uVar7 = uVar6 >> 2; uVar7 != 0; uVar7 = uVar7 - 1) {
          *(undefined4 *)pcVar8 = *(undefined4 *)pcVar5;
          pcVar5 = pcVar5 + 4;
          pcVar8 = pcVar8 + 4;
        }
        for (uVar6 = uVar6 & 3; uVar6 != 0; uVar6 = uVar6 - 1) {
          *pcVar8 = *pcVar5;
          pcVar5 = pcVar5 + 1;
          pcVar8 = pcVar8 + 1;
        }
      }
    }
  }
  return 0;
}
