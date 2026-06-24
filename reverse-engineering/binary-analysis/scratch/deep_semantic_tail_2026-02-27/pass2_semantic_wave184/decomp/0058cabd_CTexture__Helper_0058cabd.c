/* address: 0x0058cabd */
/* name: CTexture__Helper_0058cabd */
/* signature: void __thiscall CTexture__Helper_0058cabd(void * this, void * param_1, int param_2, void * param_3) */


void __thiscall CTexture__Helper_0058cabd(void *this,void *param_1,int param_2,void *param_3)

{
  char *pcVar1;
  undefined1 local_104 [256];

  switch(*(undefined4 *)param_2) {
  case 0:
    pcVar1 = "version token";
    break;
  case 1:
    goto LAB_0058cb60;
  case 2:
    pcVar1 = "integer \'%u\'";
    goto LAB_0058cb65;
  case 3:
    pcVar1 = "integer \'%dl\'";
    goto LAB_0058cb65;
  case 4:
    pcVar1 = "integer \'%uul\'";
    goto LAB_0058cb65;
  case 5:
    pcVar1 = "float \'%g\'";
    goto LAB_0058cb47;
  case 6:
    pcVar1 = "float \'%gh\'";
    goto LAB_0058cb47;
  case 7:
    pcVar1 = "float \'%gf\'";
    goto LAB_0058cb47;
  case 8:
    pcVar1 = "float \'%gl\'";
LAB_0058cb47:
    CTexture__Helper_005d075f(local_104,0x100,pcVar1);
    goto LAB_0058cba9;
  case 9:
LAB_0058cb60:
    pcVar1 = "token \'%s\'";
LAB_0058cb65:
    CTexture__Helper_005d075f(local_104,0x100,pcVar1);
    goto LAB_0058cba9;
  case 10:
    pcVar1 = "string constant";
    break;
  default:
    pcVar1 = "token";
    break;
  case 0xc:
    pcVar1 = "end of line";
    break;
  case 0xd:
    pcVar1 = "end of file";
  }
  CTexture__Helper_005d075f(local_104,0x100,pcVar1);
LAB_0058cba9:
  CTexture__Helper_0058c893(this,param_2,(int)param_1,0x5ea750);
  return;
}
