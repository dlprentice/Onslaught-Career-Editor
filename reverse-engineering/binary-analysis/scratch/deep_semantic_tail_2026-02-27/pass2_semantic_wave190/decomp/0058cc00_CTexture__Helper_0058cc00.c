/* address: 0x0058cc00 */
/* name: CTexture__Helper_0058cc00 */
/* signature: int __fastcall CTexture__Helper_0058cc00(void * param_1) */


int __fastcall CTexture__Helper_0058cc00(void *param_1)

{
  char cVar1;
  char *pcVar2;
  char *pcVar3;
  uint uVar4;
  char *extraout_ECX;
  char *extraout_ECX_00;
  char *this;
  int unaff_EDI;
  int local_8;

  local_8 = 0;
  this = param_1;
  if (*(uint *)((int)param_1 + 4) <= *(uint *)param_1) {
    return 0;
  }
  do {
    pcVar3 = *(char **)param_1;
    cVar1 = *pcVar3;
    if (cVar1 == '\n') {
      *(int *)((int)param_1 + 0x1c) = *(int *)((int)param_1 + 0x1c) + 1;
      *(char **)param_1 = pcVar3 + 1;
      local_8 = 1;
    }
    else if (cVar1 == '\\') {
      this = pcVar3 + 1;
      if ((this < *(char **)((int)param_1 + 4)) && (*this == '\n')) {
        pcVar3 = pcVar3 + 2;
      }
      else {
        this = pcVar3 + 2;
        if ((*(char **)((int)param_1 + 4) <= this) || ((pcVar3[1] != '\r' || (*this != '\n'))))
        goto LAB_0058cc6e;
        pcVar3 = pcVar3 + 3;
      }
      *(int *)((int)param_1 + 0x1c) = *(int *)((int)param_1 + 0x1c) + 1;
      *(char **)param_1 = pcVar3;
    }
    else {
LAB_0058cc6e:
      pcVar3 = (char *)(int)cVar1;
      uVar4 = CRT__IsCharTypeMask0x08(this,(char *)(int)cVar1,unaff_EDI);
      this = pcVar3;
      if (uVar4 == 0) {
        pcVar3 = *(char **)param_1;
        cVar1 = *pcVar3;
        if (cVar1 != '\r') {
          if ((((cVar1 == '/') && (pcVar3 + 1 < *(char **)((int)param_1 + 4))) && (pcVar3[1] == '/')
              ) || (((*(byte *)((int)param_1 + 0x28) & 2) != 0 && (cVar1 == ';')))) {
            CTexture__SkipLineContinuationAndAdvance(param_1);
            this = extraout_ECX;
          }
          else {
            if (cVar1 != '/') {
              return local_8;
            }
            pcVar2 = *(char **)((int)param_1 + 4);
            this = pcVar3 + 1;
            if (pcVar2 <= this) {
              return local_8;
            }
            if (*this != '*') {
              return local_8;
            }
            *(char **)param_1 = pcVar3 + 2;
            if (pcVar3 + 2 < pcVar2) {
              do {
                pcVar3 = *(char **)param_1;
                if (((*pcVar3 == '*') && (this = pcVar3 + 1, this < pcVar2)) && (*this == '/'))
                break;
                if (*pcVar3 == '\n') {
                  *(int *)((int)param_1 + 0x1c) = *(int *)((int)param_1 + 0x1c) + 1;
                }
                *(char **)param_1 = pcVar3 + 1;
              } while (pcVar3 + 1 < *(char **)((int)param_1 + 4));
            }
            if (*(char **)param_1 < pcVar2) {
              *(char **)param_1 = *(char **)param_1 + 2;
            }
            else {
              CTexture__Helper_0058c893
                        (*(void **)((int)param_1 + 0x30),(int)param_1 + 8,0x3e9,0x5ea81c);
              this = extraout_ECX_00;
            }
          }
          goto LAB_0058cd1e;
        }
      }
      *(int *)param_1 = *(int *)param_1 + 1;
    }
LAB_0058cd1e:
    if (*(uint *)((int)param_1 + 4) <= *(uint *)param_1) {
      return local_8;
    }
  } while( true );
}
