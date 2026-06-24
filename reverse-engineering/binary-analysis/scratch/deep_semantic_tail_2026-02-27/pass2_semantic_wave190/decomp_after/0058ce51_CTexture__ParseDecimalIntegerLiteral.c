/* address: 0x0058ce51 */
/* name: CTexture__ParseDecimalIntegerLiteral */
/* signature: int __thiscall CTexture__ParseDecimalIntegerLiteral(void * this, void * param_1, void * param_2, void * param_3) */


int __thiscall
CTexture__ParseDecimalIntegerLiteral(void *this,void *param_1,void *param_2,void *param_3)

{
  bool bVar1;
  void *this_00;
  uint uVar2;
  uint uVar3;
  char *pcVar4;
  int unaff_ESI;
  int unaff_EDI;

  if (param_1 < *(void **)((int)this + 4)) {
    this_00 = (void *)(int)*(char *)param_1;
    uVar2 = CRT__IsDigit_0056a089(this,this_00,unaff_EDI);
    if (uVar2 != 0) {
      uVar2 = 0;
      bVar1 = false;
      pcVar4 = param_1;
      if (param_1 < *(void **)((int)this + 4)) {
        do {
          uVar3 = CRT__IsDigit_0056a089(this_00,(void *)(int)*pcVar4,unaff_ESI);
          if (uVar3 == 0) break;
          if (0x19999999 < uVar2) {
            bVar1 = true;
          }
          this_00 = (void *)(int)*pcVar4;
          uVar3 = uVar2 * 10;
          uVar2 = (int)this_00 + (uVar3 - 0x30);
          if (uVar2 < uVar3) {
            bVar1 = true;
          }
          pcVar4 = pcVar4 + 1;
        } while (pcVar4 < *(char **)((int)this + 4));
      }
      if (param_2 != (void *)0x0) {
        *(uint *)param_2 = uVar2;
      }
      if (bVar1) {
        CTexture__AppendDiagnosticMessage(*(void **)((int)this + 0x30),(int)this + 8,0x3ec,0x5ea880)
        ;
      }
      return (int)pcVar4 - (int)param_1;
    }
  }
  return 0;
}
