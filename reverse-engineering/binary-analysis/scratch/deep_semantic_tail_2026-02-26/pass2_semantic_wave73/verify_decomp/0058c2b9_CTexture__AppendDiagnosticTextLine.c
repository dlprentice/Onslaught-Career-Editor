/* address: 0x0058c2b9 */
/* name: CTexture__AppendDiagnosticTextLine */
/* signature: int __thiscall CTexture__AppendDiagnosticTextLine(void * this, void * param_1, void * param_2) */


int __thiscall CTexture__AppendDiagnosticTextLine(void *this,void *param_1,void *param_2)

{
  char cVar1;
  char *pcVar2;
  undefined4 *extraout_EAX;
  int iVar3;
  uint uVar4;
  undefined4 *puVar5;

  iVar3 = (int)param_1 + 1;
  pcVar2 = param_1;
  do {
    cVar1 = *pcVar2;
    pcVar2 = pcVar2 + 1;
  } while (cVar1 != '\0');
  CFastVB__Helper_00426fd0((int)(pcVar2 + (5 - iVar3)));
  if (extraout_EAX == (undefined4 *)0x0) {
    iVar3 = -0x7ff8fff2;
  }
  else {
    *extraout_EAX = *(undefined4 *)this;
    *(int *)((int)this + 4) = (int)(pcVar2 + (*(int *)((int)this + 4) - iVar3));
    *(undefined4 **)this = extraout_EAX;
    puVar5 = extraout_EAX;
    for (uVar4 = (uint)(pcVar2 + (1 - iVar3)) >> 2; puVar5 = puVar5 + 1, uVar4 != 0;
        uVar4 = uVar4 - 1) {
      *puVar5 = *(undefined4 *)param_1;
      param_1 = (undefined4 *)((int)param_1 + 4);
    }
    for (uVar4 = (uint)(pcVar2 + (1 - iVar3)) & 3; uVar4 != 0; uVar4 = uVar4 - 1) {
      *(undefined1 *)puVar5 = *(undefined1 *)param_1;
      param_1 = (undefined4 *)((int)param_1 + 1);
      puVar5 = (undefined4 *)((int)puVar5 + 1);
    }
    iVar3 = 0;
  }
  return iVar3;
}
