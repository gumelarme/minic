int result;
int b;

int power(int n){
  if(n==0){
    return 1;
  }else{
    return n * power(n-1);
  }
}

void main(int a){
  result = power(5);
}
