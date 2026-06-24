/* address: 0x0056bba5 */
/* name: CFastVB__NormalizeDigitStringInPlace */
/* signature: void __cdecl CFastVB__NormalizeDigitStringInPlace(void * param_1) */


void __cdecl CFastVB__NormalizeDigitStringInPlace(void *param_1)

{
  char *pcVar1;
  char cVar2;
  char *pcVar3;

  cVar2 = *(char *)param_1;
  do {
    if (cVar2 == '\0') {
      return;
    }
    if ((cVar2 < '0') || ('9' < cVar2)) {
      pcVar3 = param_1;
      if (cVar2 != ';') goto LAB_0056bbbc;
      do {
        pcVar1 = pcVar3 + 1;
        *pcVar3 = pcVar3[1];
        pcVar3 = pcVar1;
      } while (*pcVar1 != '\0');
    }
    else {
      *(char *)param_1 = cVar2 + -0x30;
LAB_0056bbbc:
      param_1 = (void *)((int)param_1 + 1);
    }
    cVar2 = *(char *)param_1;
  } while( true );
}
